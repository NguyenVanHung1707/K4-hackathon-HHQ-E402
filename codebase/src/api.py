import hashlib
import json
import os
import random
import re
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

try:
    from codebase.src.config import get_settings
    from codebase.src.generator import QuizGenerator
    from codebase.src.grader import AutoGrader
    from codebase.src.analytics import KnowledgeAnalytics
    from codebase.src.vector_store import RAGVectorStore
    from codebase.src.denoiser import TranscriptDenoiser
    from codebase.src.db import SQLiteDatabase
except ImportError:
    from config import get_settings
    from generator import QuizGenerator
    from grader import AutoGrader
    from analytics import KnowledgeAnalytics
    from vector_store import RAGVectorStore
    from denoiser import TranscriptDenoiser
    from db import SQLiteDatabase

app = FastAPI(
    title="VLearn EduAI API Engine",
    description="Hệ thống Học tập Chủ động & Thích ứng (Student-Triggered Generation & Sequential Gating)",
    version="3.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = QuizGenerator()
grader = AutoGrader()
analytics = KnowledgeAnalytics()
vector_store = RAGVectorStore()
denoiser = TranscriptDenoiser()
db = SQLiteDatabase()
_SLIDE_PAGE_CONTEXT_CACHE: Dict[str, Dict[str, Any]] = {}
_TRANSCRIPT_CONTEXT_CACHE: Dict[str, Dict[str, Any]] = {}
_LESSON_SUMMARY_CACHE: Dict[str, Dict[str, Any]] = {}
QUIZ_GENERATION_VERSION = 4
LESSON_SUMMARY_VERSION = 1


def _slide_cache_signature(slide_dir: str, max_pages: int, chars_per_page: int) -> str:
    parts = [f"max_pages={max_pages}", f"chars={chars_per_page}"]
    for filename in sorted(os.listdir(slide_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(slide_dir, filename)
        stat = os.stat(pdf_path)
        parts.append(f"{filename}:{stat.st_size}:{int(stat.st_mtime)}")
    return "|".join(parts)


def _extract_slide_page_context(session_id: str, max_pages: int = 8, chars_per_page: int = 800) -> Dict[str, Any]:
    """Read local slide PDFs and return page-level context with citations."""
    slide_dir = os.path.join(get_settings().data_dir, session_id, "Slide")
    if not os.path.exists(slide_dir):
        return {"context": "", "citations": []}

    signature = _slide_cache_signature(slide_dir, max_pages, chars_per_page)
    memory_key = f"{session_id}:{signature}"
    if memory_key in _SLIDE_PAGE_CONTEXT_CACHE:
        return _SLIDE_PAGE_CONTEXT_CACHE[memory_key]

    cache_dir = os.path.join(get_settings().data_dir, "cache", "slide_pages")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{session_id}.json")
    stale_cached_result = None
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as fp:
                cached = json.load(fp)
            stale_cached_result = cached.get("result")
            if cached.get("signature") == signature:
                result = cached.get("result", {"context": "", "citations": []})
                _SLIDE_PAGE_CONTEXT_CACHE[memory_key] = result
                return result
        except Exception as e:
            print(f"[Warning] Cannot read slide cache {cache_path}: {e}")

    try:
        from pypdf import PdfReader
    except Exception as e:
        print(f"[Warning] pypdf unavailable, skipping slide page citations: {e}")
        return stale_cached_result or {"context": "", "citations": []}

    chunks = []
    citations = []
    pages_read = 0
    for filename in sorted(os.listdir(slide_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(slide_dir, filename)
        try:
            reader = PdfReader(pdf_path)
            for page_idx, page in enumerate(reader.pages):
                if pages_read >= max_pages:
                    break
                text = (page.extract_text() or "").strip()
                if len(text) < 30:
                    continue
                citation = f"[Slide {session_id} trang {page_idx + 1}]"
                citations.append(citation)
                chunks.append(f"{citation}\n{text[:chars_per_page]}")
                pages_read += 1
            if pages_read >= max_pages:
                break
        except Exception as e:
            print(f"[Warning] Cannot read slide PDF {pdf_path}: {e}")

    result = (
        {"context": "\n---\n".join(chunks), "citations": citations}
        if chunks
        else stale_cached_result or {"context": "", "citations": []}
    )
    _SLIDE_PAGE_CONTEXT_CACHE[memory_key] = result
    try:
        with open(cache_path, "w", encoding="utf-8") as fp:
            json.dump({"signature": signature, "result": result}, fp, ensure_ascii=False)
    except Exception as e:
        print(f"[Warning] Cannot write slide cache {cache_path}: {e}")
    return result


def _content_terms(text: str) -> set:
    stopwords = {
        "các", "cho", "của", "được", "giảng", "học", "không", "làm",
        "một", "những", "này", "nội", "phần", "slide", "thành", "theo",
        "trong", "trang", "trình", "và", "vào", "với", "day", "transcript",
        "the", "and", "for", "from", "that", "this", "with",
    }
    return {
        token
        for token in re.findall(r"[^\W\d_]{3,}", text.casefold(), flags=re.UNICODE)
        if token not in stopwords
    }


def _transcript_cache_signature(script_dir: str) -> str:
    parts = []
    for filename in sorted(os.listdir(script_dir)):
        if not filename.lower().endswith((".md", ".txt")):
            continue
        path = os.path.join(script_dir, filename)
        stat = os.stat(path)
        parts.append(f"{filename}:{stat.st_size}:{int(stat.st_mtime)}")
    return "|".join(parts)


def _extract_filtered_transcript_context(
    session_id: str,
    slide_context: str,
    max_chunks: int = 8,
    chars_per_chunk: int = 900,
) -> Dict[str, Any]:
    """Filter transcript noise/injections, then retain only slide-related chunks."""
    script_dir = os.path.join(get_settings().data_dir, session_id, "Script")
    if not os.path.isdir(script_dir):
        return {
            "context": "",
            "citations": [],
            "candidate_chunks": 0,
            "selected_chunks": 0,
        }

    signature = _transcript_cache_signature(script_dir)
    cache_key = f"{session_id}:{signature}:{hash(slide_context)}:{max_chunks}:{chars_per_chunk}"
    if cache_key in _TRANSCRIPT_CONTEXT_CACHE:
        return _TRANSCRIPT_CONTEXT_CACHE[cache_key]

    session_topic_hints = {
        "Day01": (
            "AI machine learning deep learning generative LLM transformer "
            "attention token model agent API foundation"
        ),
        "Day02": (
            "problem discovery statement double diamond HCD PAIR automate "
            "augment workflow agent reward success criteria metric risk "
            "human loop user pain point solution validation"
        ),
    }
    scope_text = slide_context or session_topic_hints.get(session_id, session_id)
    slide_terms = _content_terms(scope_text)
    minimum_overlap = 2 if slide_context.strip() else 1
    ranked_chunks = []
    candidate_count = 0

    for filename in sorted(os.listdir(script_dir)):
        if not filename.lower().endswith((".md", ".txt")):
            continue
        path = os.path.join(script_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                raw_text = fp.read()
        except Exception as exc:
            print(f"[Warning] Cannot read transcript {path}: {exc}")
            continue

        for chunk_index, raw_chunk in enumerate(
            re.split(r"\n\s*\n", raw_text),
            start=1,
        ):
            denoised = denoiser.denoise_transcript(raw_chunk)
            cleaned = denoised.get("cleaned_transcript", "").strip()
            if len(cleaned) < 80:
                continue

            candidate_count += 1
            overlap = slide_terms.intersection(_content_terms(cleaned))
            if len(overlap) < minimum_overlap:
                continue

            marker_match = re.search(r"\[(T\d+-\d+)\]", cleaned, re.IGNORECASE)
            marker = marker_match.group(1).upper() if marker_match else f"đoạn {chunk_index}"
            source_name = os.path.splitext(filename)[0]
            citation = f"[Transcript {session_id} {source_name} {marker}]"
            relevance = len(overlap) + min(len(cleaned) / 1000, 1)
            ranked_chunks.append((relevance, citation, cleaned[:chars_per_chunk]))

    ranked_chunks.sort(key=lambda item: item[0], reverse=True)
    selected = []
    seen = set()
    for _, citation, text in ranked_chunks:
        dedupe_key = re.sub(r"\s+", " ", text.casefold())[:160]
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        selected.append((citation, text))
        if len(selected) >= max_chunks:
            break

    result = {
        "context": "\n---\n".join(
            f"{citation}\n{text}" for citation, text in selected
        ),
        "citations": [citation for citation, _ in selected],
        "candidate_chunks": candidate_count,
        "selected_chunks": len(selected),
    }
    _TRANSCRIPT_CONTEXT_CACHE[cache_key] = result
    return result


def _summary_signature(
    session_id: str,
    slide_context: str,
) -> str:
    script_dir = os.path.join(get_settings().data_dir, session_id, "Script")
    transcript_signature = (
        _transcript_cache_signature(script_dir)
        if os.path.isdir(script_dir)
        else ""
    )
    raw = "|".join([
        str(LESSON_SUMMARY_VERSION),
        session_id,
        transcript_signature,
        slide_context,
        get_settings().llm_provider,
        get_settings().llm_model_name,
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _summary_items(
    raw_items: Any,
    allowed_citations: List[str],
    limit: int,
) -> List[Dict[str, str]]:
    if not isinstance(raw_items, list) or not allowed_citations:
        return []

    normalized = []
    for index, raw_item in enumerate(raw_items):
        if isinstance(raw_item, dict):
            text = str(raw_item.get("text", "")).strip()
            citation = str(raw_item.get("citation", "")).strip()
        else:
            text = str(raw_item).strip()
            citation = ""
        if not text:
            continue
        if citation not in allowed_citations:
            citation = allowed_citations[index % len(allowed_citations)]
        normalized.append({"text": text, "citation": citation})
        if len(normalized) >= limit:
            break
    return normalized


def _extractive_lesson_summary(
    session_title: str,
    transcript_context: Dict[str, Any],
) -> Dict[str, Any]:
    points = []
    for block in transcript_context.get("context", "").split("\n---\n"):
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        citation = lines[0].strip()
        body = re.sub(r"\*\*\[T\d+-\d+\]\*\*\s*", "", " ".join(lines[1:]))
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", body)
            if len(sentence.strip()) >= 50
        ]
        if sentences:
            points.append({
                "text": sentences[0][:360],
                "citation": citation,
            })
        if len(points) >= 6:
            break

    overview = " ".join(point["text"] for point in points[:2])
    return {
        "title": session_title,
        "overview": overview or "Chưa đủ nội dung transcript phù hợp để tạo bản tóm tắt.",
        "key_points": points,
        "concepts": [],
        "practical_examples": [],
        "summary_method": "extractive_fallback",
    }


def _normalize_lesson_summary(
    raw_summary: Dict[str, Any],
    session_title: str,
    transcript_context: Dict[str, Any],
) -> Dict[str, Any]:
    transcript_citations = transcript_context.get("citations", [])
    fallback = _extractive_lesson_summary(session_title, transcript_context)
    if not isinstance(raw_summary, dict) or not raw_summary:
        summary = fallback
    else:
        key_points = _summary_items(
            raw_summary.get("key_points"),
            transcript_citations,
            7,
        )
        practical_examples = _summary_items(
            raw_summary.get("practical_examples"),
            transcript_citations,
            4,
        )
        concepts = raw_summary.get("concepts", [])
        concepts = [
            str(concept).strip()
            for concept in concepts
            if str(concept).strip()
        ][:8] if isinstance(concepts, list) else []
        overview = str(raw_summary.get("overview", "")).strip()
        summary = {
            "title": str(raw_summary.get("title", "")).strip() or session_title,
            "overview": overview or fallback["overview"],
            "key_points": key_points or fallback["key_points"],
            "concepts": concepts,
            "practical_examples": practical_examples,
            "summary_method": "llm",
        }

    summary["sources"] = list(dict.fromkeys(
        item["citation"]
        for section in ("key_points", "practical_examples")
        for item in summary.get(section, [])
        if item.get("citation")
    ))
    summary["source_diagnostics"] = {
        "transcript_candidates": transcript_context.get("candidate_chunks", 0),
        "transcript_chunks_used": transcript_context.get("selected_chunks", 0),
    }
    return summary


def _ensure_question_citations(
    quiz_data: Dict[str, Any],
    fallback_citations: List[str],
    allowed_citations: List[str] = None,
) -> Dict[str, Any]:
    """Preserve concrete slide/transcript citations and repair generic ones."""
    if not fallback_citations:
        return quiz_data

    allowed = set(allowed_citations or fallback_citations)
    for idx, question in enumerate(quiz_data.get("questions", [])):
        citation = str(question.get("citation", "")).strip()
        if citation not in allowed:
            question["citation"] = fallback_citations[idx % len(fallback_citations)]
    return quiz_data


def _grounded_review_questions(review_questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        question for question in review_questions
        if any(
            source in str(question.get("citation", "")).lower()
            for source in ("slide", "transcript")
        )
    ]


def _default_type_counts(total_questions: int) -> Dict[str, int]:
    if total_questions <= 0:
        return {"multiple_choice": 1, "fill_in_blank": 1, "short_essay": 1}
    base = {
        "multiple_choice": max(1, total_questions // 3),
        "fill_in_blank": max(1, total_questions // 3),
        "short_essay": max(1, total_questions // 3),
    }
    while sum(base.values()) < total_questions:
        base["multiple_choice"] += 1
    while sum(base.values()) > total_questions:
        for q_type in ["multiple_choice", "fill_in_blank", "short_essay"]:
            if base[q_type] > 0 and sum(base.values()) > total_questions:
                base[q_type] -= 1
    return base


def _normalize_type_counts(type_counts: Any, num_questions: int) -> Dict[str, int]:
    allowed = ["multiple_choice", "fill_in_blank", "short_essay"]
    if not isinstance(type_counts, dict):
        return _default_type_counts(num_questions)

    normalized = {}
    for q_type in allowed:
        try:
            count = int(type_counts.get(q_type, 0) or 0)
        except Exception:
            count = 0
        if count > 0:
            normalized[q_type] = min(count, 20)

    return normalized or _default_type_counts(num_questions)


def _select_quiz_from_bank(
    bank_questions: List[Dict[str, Any]],
    session_id: str,
    session_title: str,
    difficulty: str,
    type_counts: Dict[str, int],
    review_questions: List[Dict[str, Any]],
    slide_citations: List[str],
    source_citations: List[str] = None,
    excluded_question_texts: List[str] = None
) -> Dict[str, Any]:
    selected = []
    used = set()
    excluded = {text.strip() for text in (excluded_question_texts or []) if text and text.strip()}
    rng = random.SystemRandom()
    for q_type, target_count in type_counts.items():
        matches = [
            (idx, question)
            for idx, question in enumerate(bank_questions)
            if question.get("type") == q_type and idx not in used and not _is_placeholder_question(question)
        ]
        fresh_matches = [
            item for item in matches
            if str(item[1].get("question_text") or item[1].get("question") or "").strip() not in excluded
        ]
        if len(fresh_matches) >= target_count:
            matches = fresh_matches
        rng.shuffle(matches)
        for idx, question in matches[:target_count]:
            selected.append(dict(question))
            used.add(idx)

    quiz_data = {
        "status": "success",
        "session_name": session_title,
        "source": "question_bank",
        "setup": {
            "type_counts": type_counts,
            "difficulty": difficulty
        },
        "total_questions": len(selected),
        "questions": selected
    }
    allow_fallback_questions = sum(type_counts.values()) > 10
    quiz_data = generator._finalize_quiz(
        quiz_data,
        review_questions,
        session_title,
        difficulty,
        type_counts,
        allow_fallback_questions
    )
    quiz_data = _ensure_question_citations(
        quiz_data,
        slide_citations,
        source_citations,
    )
    for idx, question in enumerate(quiz_data.get("questions", []), 1):
        question["id"] = f"Q{idx}"
        question.setdefault("bank_session_id", session_id)
    return quiz_data


def _is_placeholder_question(question: Dict[str, Any]) -> bool:
    if question.get("is_fallback_generated"):
        return True
    text = str(question.get("question_text") or question.get("question") or "").lower()
    return any(
        marker in text
        for marker in ("bo sung", "bổ sung", "chuyen sau", "chuyên sâu", "concept-")
    )


def _usable_bank_questions(bank_questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [question for question in bank_questions if not _is_placeholder_question(question)]


def _bank_generation_counts(
    bank_questions: List[Dict[str, Any]],
    type_counts: Dict[str, int],
    excluded_question_texts: List[str] = None
) -> Dict[str, int]:
    """Return only the small bank refill needed for the current request."""
    bank_questions = _usable_bank_questions(bank_questions)
    excluded = {
        text.strip()
        for text in (excluded_question_texts or [])
        if text and text.strip()
    }
    small_quiz = sum(type_counts.values()) <= 10
    generation_counts = {}

    for q_type, requested_count in type_counts.items():
        matching = [q for q in bank_questions if q.get("type") == q_type]
        fresh_count = sum(
            1
            for question in matching
            if str(question.get("question_text") or question.get("question") or "").strip()
            not in excluded
        )
        if fresh_count >= requested_count:
            continue

        # Keep one spare for common small quizzes without generating a huge bank.
        target_bank_size = requested_count + (1 if small_quiz else 0)
        generation_counts[q_type] = max(
            requested_count - fresh_count,
            target_bank_size - len(matching),
        )

    return generation_counts


def _merge_question_bank(
    existing_questions: List[Dict[str, Any]],
    new_questions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    merged = []
    seen = set()
    for question in existing_questions + new_questions:
        text = str(question.get("question_text") or question.get("question") or "").strip()
        key = (question.get("type"), text.casefold())
        if not text or key in seen or _is_placeholder_question(question):
            continue
        seen.add(key)
        merged.append(question)
    return merged


def _current_session_bank_questions(
    bank_questions: List[Dict[str, Any]],
    session_id: str
) -> List[Dict[str, Any]]:
    return [
        question
        for question in _usable_bank_questions(bank_questions)
        if question.get("bank_session_id") == session_id
        and question.get("generation_version") == QUIZ_GENERATION_VERSION
    ]


def _stamp_bank_questions(
    questions: List[Dict[str, Any]],
    session_id: str
) -> List[Dict[str, Any]]:
    stamped = []
    for question in questions:
        item = dict(question)
        item["bank_session_id"] = session_id
        item["generation_version"] = QUIZ_GENERATION_VERSION
        stamped.append(item)
    return stamped


def _option_content(option: Any) -> str:
    text = str(option).strip()
    if len(text) >= 3 and text[0].upper() in "ABCD" and text[1] in ".):":
        return text[2:].strip()
    return text


def _balance_correct_answer_positions(
    quiz_data: Dict[str, Any],
    session_id: str,
    student_id: str
) -> Dict[str, Any]:
    """Cycle MCQ answers through A-D while preserving the correct option text."""
    mc_index = 0
    offset = sum(ord(char) for char in f"{session_id}:{student_id}") % 4

    for question in quiz_data.get("questions", []):
        options = question.get("options") or []
        if question.get("type") != "multiple_choice" or len(options) < 2:
            continue

        correct_answer = str(question.get("correct_answer", "")).strip()
        correct_content = _option_content(correct_answer)
        option_contents = [_option_content(option) for option in options]
        correct_index = next(
            (
                idx
                for idx, option in enumerate(options)
                if str(option).strip() == correct_answer
                or option_contents[idx].casefold() == correct_content.casefold()
            ),
            None,
        )
        if (
            correct_index is None
            and correct_answer
            and correct_answer[:1].upper() in "ABCD"
        ):
            candidate_index = ord(correct_answer[:1].upper()) - ord("A")
            if candidate_index < len(options):
                correct_index = candidate_index
                correct_content = option_contents[candidate_index]
        if correct_index is None:
            continue

        desired_index = (offset + mc_index) % len(options)
        distractors = [
            content
            for idx, content in enumerate(option_contents)
            if idx != correct_index
        ]
        reordered = list(distractors)
        reordered.insert(desired_index, correct_content)
        labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        question["options"] = [
            f"{labels[idx]}. {content}"
            for idx, content in enumerate(reordered)
        ]
        question["correct_answer"] = f"{labels[desired_index]}. {correct_content}"
        mc_index += 1

    return quiz_data


@app.get("/")
@app.get("/api/v1/health")
def read_root():
    return {
        "status": "ok",
        "app": "VLearn EduAI Engine v3.5 (Direct Entry & Student Setup)",
        "vector_store_status": "ready",
        "sqlite_db_status": "connected",
        "sqlite_db_path": db.db_path
    }


# =====================================================================
# 1. YÊU CẦU CHO TEACHER (Loại bỏ Generation - Chỉ Upload Học Liệu & Analytics)
# =====================================================================

@app.post("/api/teacher/materials")
@app.post("/api/teacher/upload")
@app.post("/api/v1/ingest")
def teacher_materials(payload: Dict[str, Any] = Body(...)):
    """
    POST /api/teacher/materials
    Nhận file upload, xử lý chunking, embedding và lưu vào Vector DB.
    Hỗ trợ 3 chế độ: 'new' (Tạo Day mới), 'append' (Bổ sung học liệu), 'overwrite' (Thay thế học liệu cũ).
    """
    target_day = payload.get("target_day") or payload.get("transcript_id") or payload.get("module_id") or "Day01"
    upload_mode = payload.get("upload_mode", "append")  # 'new' | 'append' | 'overwrite'
    transcript_text = payload.get("transcript_text") or payload.get("sourceText") or payload.get("text", "")
    slide_text = payload.get("slide_text", "")
    session_title = payload.get("session_title") or payload.get("session") or f"Buổi học {target_day}"

    # 1. LLM Denoising & Chunking
    cleaned = denoiser.denoise_transcript(transcript_text) if transcript_text else {}
    clean_text = cleaned.get("cleaned_transcript", transcript_text)

    # 2. Embedding & Vector DB Storage (No LLM Question Generation)
    t_count = vector_store.ingest_transcript(target_day, clean_text) if clean_text else 0
    s_count = vector_store.ingest_slide(f"SLIDE-{target_day}", slide_text) if slide_text else 0

    # 3. Save / Update module metadata into SQLite DB
    mode_str = "Tạo mới" if upload_mode == "new" else ("Thay thế" if upload_mode == "overwrite" else "Bổ sung")
    db.save_module(
        module_id=target_day,
        title=session_title,
        session=f"Session {target_day}",
        description=f"Học liệu nguyên bản ({mode_str}). Đã nạp {len(clean_text)} kí tự vào Vector DB.",
        questions=[]
    )

    return {
        "status": "success",
        "message": f"Đã {mode_str} học liệu vào {target_day} thành công! (Nạp {t_count} chunks vào Vector DB).",
        "module_id": target_day,
        "upload_mode": upload_mode,
        "chunks_ingested": t_count,
        "slide_sections_ingested": s_count
    }


@app.get("/api/teacher/analytics/{class_id}")
@app.get("/api/teacher/analytics")
@app.get("/api/v1/analytics-report")
def teacher_analytics(class_id: str = "CS101"):
    """GET /api/teacher/analytics/{class_id}: Trả về JSON thống kê năng lực sinh viên thực tế & bản đồ lỗ hổng."""
    submissions = db.get_all_submissions()
    return analytics.generate_class_report(submissions or [])


# =====================================================================
# 2. YÊU CẦU CHO STUDENT (Direct Entry, Setup Popup & Student-Triggered)
# =====================================================================

@app.post("/api/student/login")
def student_login(payload: Dict[str, Any] = Body(...)):
    """POST /api/student/login: Tự động đăng ký / khởi tạo hồ sơ học tập riêng cho sinh viên."""
    student_id = payload.get("studentId") or payload.get("student_id") or "2012345"
    full_name = payload.get("fullName") or payload.get("student_name") or "Nguyễn Văn A"

    prog = db.get_student_session_progress(student_id, "Day01")
    if not prog or prog.get("status") == "locked":
        db.update_student_session_progress(
            student_id=student_id,
            session_id="Day01",
            status="unlocked",
            score=0.0,
            weak_concepts=[]
        )

    return {
        "status": "success",
        "message": f"Chào mừng sinh viên {full_name} (MSSV: {student_id})!",
        "student": {
            "student_id": student_id,
            "full_name": full_name
        }
    }


@app.get("/api/student/session/{session_id}/quiz")
def get_student_session_quiz(session_id: str, student_id: str = "2012345"):
    """GET /api/student/session/{session_id}/quiz: Kiểm tra bộ câu hỏi đã tạo trước đó."""
    all_modules = db.get_all_modules()
    module_ids = [m["module_id"] for m in all_modules]
    current_idx = module_ids.index(session_id) if session_id in module_ids else 0

    # Sequential Gating Middleware: Check session N-1
    if current_idx > 0:
        prev_session_id = module_ids[current_idx - 1]
        prev_progress = db.get_student_session_progress(student_id, prev_session_id)
        if prev_progress.get("status") != "completed":
            raise HTTPException(
                status_code=403,
                detail=f"403 Forbidden: Yêu cầu hoàn thành bài tập buổi trước ({prev_session_id}) mới được mở khóa buổi {session_id}!"
            )

    # Check if existing generated quiz exists for (student_id, session_id)
    quiz_key = f"{student_id}_{session_id}"
    existing_quiz = db.get_quiz(quiz_key)

    if (
        existing_quiz
        and existing_quiz.get("content_source") == "slides_and_filtered_transcript"
        and existing_quiz.get("generation_version") == QUIZ_GENERATION_VERSION
        and existing_quiz.get("questions")
        and len(existing_quiz.get("questions")) > 0
    ):
        return {
            "status": "success",
            "has_existing": True,
            "session_id": session_id,
            "student_id": student_id,
            "source_diagnostics": existing_quiz.get("source_diagnostics", {}),
            "questions": existing_quiz.get("questions")
        }

    return {
        "status": "needs_setup",
        "has_existing": False,
        "session_id": session_id,
        "student_id": student_id,
        "questions": []
    }


@app.get("/api/student/session/{session_id}/summary")
def get_student_session_summary(session_id: str, student_id: str = "2012345"):
    """Return a cached LLM summary built from filtered transcript chunks."""
    all_modules = db.get_all_modules()
    module_ids = [module["module_id"] for module in all_modules]
    if session_id not in module_ids:
        raise HTTPException(status_code=404, detail="Không tìm thấy buổi học.")

    module = db.get_module_by_id(session_id)
    session_title = module.get("title", session_id) if module else session_id
    slide_context = _extract_slide_page_context(session_id)
    transcript_context = _extract_filtered_transcript_context(
        session_id,
        slide_context.get("context", ""),
        max_chunks=12,
        chars_per_chunk=1200,
    )
    if not transcript_context.get("context"):
        raise HTTPException(
            status_code=422,
            detail="Không tìm thấy đoạn transcript phù hợp sau khi lọc.",
        )

    signature = _summary_signature(
        session_id,
        slide_context.get("context", ""),
    )
    memory_key = f"{session_id}:{signature}"
    if memory_key in _LESSON_SUMMARY_CACHE:
        return {
            "status": "success",
            "session_id": session_id,
            "cached": True,
            "summary": _LESSON_SUMMARY_CACHE[memory_key],
        }

    cache_dir = os.path.join(get_settings().data_dir, "cache", "lesson_summaries")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{session_id}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as fp:
                cached = json.load(fp)
            if cached.get("signature") == signature and cached.get("summary"):
                summary = cached["summary"]
                _LESSON_SUMMARY_CACHE[memory_key] = summary
                return {
                    "status": "success",
                    "session_id": session_id,
                    "cached": True,
                    "summary": summary,
                }
        except Exception as exc:
            print(f"[Warning] Cannot read lesson summary cache {cache_path}: {exc}")

    raw_summary = generator.generate_lesson_summary(
        session_name=session_title,
        filtered_transcript_context=transcript_context["context"],
        slide_context=slide_context.get("context", ""),
    )
    summary = _normalize_lesson_summary(
        raw_summary,
        session_title,
        transcript_context,
    )
    _LESSON_SUMMARY_CACHE[memory_key] = summary
    try:
        with open(cache_path, "w", encoding="utf-8") as fp:
            json.dump(
                {"signature": signature, "summary": summary},
                fp,
                ensure_ascii=False,
            )
    except Exception as exc:
        print(f"[Warning] Cannot write lesson summary cache {cache_path}: {exc}")

    return {
        "status": "success",
        "session_id": session_id,
        "cached": False,
        "summary": summary,
    }


@app.post("/api/student/session/{session_id}/generate-quiz")
def student_generate_quiz(session_id: str, payload: Dict[str, Any] = Body(default={})):
    """POST /api/student/session/{session_id}/generate-quiz: Gọi AI sinh đề bài cá nhân hóa thời gian thực."""
    student_id = payload.get("student_id", "2012345")
    num_questions = payload.get("num_questions") or 3
    quiz_types = payload.get("quiz_types") or "Trắc nghiệm, Điền từ, Tự luận"
    difficulty = payload.get("difficulty_level") or payload.get("difficulty") or "Cơ bản"
    type_counts = _normalize_type_counts(payload.get("type_counts"), int(num_questions))

    all_modules = db.get_all_modules()
    module_ids = [m["module_id"] for m in all_modules]
    current_idx = module_ids.index(session_id) if session_id in module_ids else 0

    # Sequential Gating Middleware Check
    if current_idx > 0:
        prev_session_id = module_ids[current_idx - 1]
        prev_progress = db.get_student_session_progress(student_id, prev_session_id)
        if prev_progress.get("status") != "completed":
            raise HTTPException(
                status_code=403,
                detail=f"403 Forbidden: Yêu cầu hoàn thành bài tập buổi trước ({prev_session_id}) mới được mở khóa buổi {session_id}!"
            )

    # Retrieve Analytics DB & Vector DB
    prev_session_id = module_ids[current_idx - 1] if current_idx > 0 else session_id
    prev_weakness = db.get_previous_session_weakness(student_id, prev_session_id)
    weak_concepts = prev_weakness.get("weak_concepts", [])
    review_questions = _grounded_review_questions(
        db.get_previous_wrong_questions(student_id, prev_session_id)
    ) if current_idx > 0 else []

    mod = db.get_module_by_id(session_id)

    # Slides define the syllabus; only filtered, slide-related transcript chunks may enrich it.
    slide_page_context = _extract_slide_page_context(session_id)
    slide_citations = slide_page_context.get("citations", [])
    transcript_context = _extract_filtered_transcript_context(
        session_id,
        slide_page_context.get("context", ""),
    )
    source_citations = slide_citations + transcript_context.get("citations", [])
    context_parts = []
    if slide_page_context.get("context"):
        context_parts.append(
            "[NGUỒN SLIDE - NGUỒN SỰ THẬT CHÍNH]\n"
            + slide_page_context["context"]
        )
    if transcript_context.get("context"):
        context_parts.append(
            "[NGUỒN TRANSCRIPT ĐÃ LỌC - CHỈ DÙNG ĐỂ GIẢI THÍCH/VÍ DỤ]\n"
            + transcript_context["context"]
        )
    retrieved_context = "\n---\n".join(context_parts)

    if not retrieved_context:
        retrieved_context = (
            f"[Slide {session_id}]\n"
            "Khong tim thay nguon hoc lieu da loc. Khong tu suy dien kien thuc ben ngoai."
        )

    session_title = mod.get("title", session_id) if mod else session_id
    quiz_key = f"{student_id}_{session_id}"
    previous_student_quiz = db.get_quiz(quiz_key)
    excluded_question_texts = [
        str(question.get("question_text") or question.get("question") or "")
        for question in (previous_student_quiz or {}).get("questions", [])
    ]
    bank_questions = _current_session_bank_questions(
        db.get_question_bank(session_id, difficulty),
        session_id,
    )
    bank_generation_counts = _bank_generation_counts(
        bank_questions,
        type_counts,
        excluded_question_texts,
    )

    if bank_generation_counts:
        bank_quiz = generator.generate_student_triggered_quiz(
            current_session_name=session_title,
            retrieved_context=retrieved_context,
            weak_concepts=[],
            num_questions=sum(bank_generation_counts.values()),
            quiz_types="Question bank refill",
            difficulty=difficulty,
            type_counts=bank_generation_counts,
            review_questions=[],
            allow_fallback_questions=False
        )
        bank_quiz = _ensure_question_citations(
            bank_quiz,
            slide_citations,
            source_citations,
        )
        bank_questions = _merge_question_bank(
            bank_questions,
            _stamp_bank_questions(bank_quiz.get("questions", []), session_id),
        )
        if bank_questions:
            db.save_question_bank(session_id, difficulty, bank_questions)

    generated_quiz = _select_quiz_from_bank(
        bank_questions=bank_questions,
        session_id=session_id,
        session_title=session_title,
        difficulty=difficulty,
        type_counts=type_counts,
        review_questions=review_questions,
        slide_citations=slide_citations,
        source_citations=source_citations,
        excluded_question_texts=excluded_question_texts
    )

    if not generated_quiz.get("questions"):
        generated_quiz = generator.generate_student_triggered_quiz(
            current_session_name=session_title,
            retrieved_context=retrieved_context,
            weak_concepts=weak_concepts,
            num_questions=int(num_questions),
            quiz_types=quiz_types,
            difficulty=difficulty,
            type_counts=type_counts,
            review_questions=review_questions,
            allow_fallback_questions=sum(type_counts.values()) > 10
        )
        generated_quiz = _ensure_question_citations(
            generated_quiz,
            slide_citations,
            source_citations,
        )

    generated_quiz = _balance_correct_answer_positions(
        generated_quiz,
        session_id,
        student_id,
    )
    generated_quiz["content_source"] = "slides_and_filtered_transcript"
    generated_quiz["generation_version"] = QUIZ_GENERATION_VERSION
    generated_quiz["source_diagnostics"] = {
        "slide_pages": len(slide_citations),
        "transcript_candidates": transcript_context.get("candidate_chunks", 0),
        "transcript_chunks_used": transcript_context.get("selected_chunks", 0),
    }

    # Purge old quiz data for this student & session before saving newly generated quiz
    db.delete_quiz(quiz_key)
    db.delete_quiz(session_id)

    # Save newly generated quiz to SQLite DB
    db.save_quiz(quiz_key, session_id, generated_quiz)
    db.save_quiz(session_id, session_id, generated_quiz)

    return {
        "status": "success",
        "session_id": session_id,
        "student_id": student_id,
        "has_existing": True,
        "setup_applied": {
            "num_questions": num_questions,
            "quiz_types": quiz_types,
            "difficulty": difficulty
        },
        "source_diagnostics": generated_quiz["source_diagnostics"],
        "questions": generated_quiz.get("questions", [])
    }


@app.post("/api/student/session/{session_id}/submit")
@app.post("/api/v1/submit-quiz")
def submit_student_session_quiz(session_id: str = "Day01", payload: Dict[str, Any] = Body(...)):
    """POST /api/student/session/{session_id}/submit: Nộp bài làm, chấm điểm & mở khóa buổi sau."""
    student_id = payload.get("student_id", "2012345")
    student_name = payload.get("student_name", "Học viên VLearn")
    transcript_id = payload.get("transcript_id") or session_id
    answers = payload.get("answers", {})

    quiz_key = f"{student_id}_{transcript_id}"
    quiz_data = db.get_quiz(quiz_key) or db.get_quiz(transcript_id) or db.get_module_by_id(transcript_id)
    if not quiz_data:
        quiz_data = generator.generate_student_triggered_quiz(transcript_id, "Context", [])

    result = grader.grade_submission(student_id, student_name, quiz_data, answers)
    result["transcript_id"] = transcript_id

    # Adaptive Weak Concepts Propagation Algorithm:
    all_modules = db.get_all_modules()
    module_ids = [m["module_id"] for m in all_modules]
    current_idx = module_ids.index(session_id) if session_id in module_ids else 0

    accumulated_weak_concepts = []
    if current_idx > 0:
        prev_session_id = module_ids[current_idx - 1]
        prev_weakness = db.get_previous_session_weakness(student_id, prev_session_id)
        accumulated_weak_concepts = list(prev_weakness.get("weak_concepts", []))

    for qr in result.get("question_results", []):
        concept = qr.get("concept", "")
        score = qr.get("score", 0.0)
        max_score = qr.get("max_score", 1.0)
        is_correct = score >= (max_score * 0.7)

        if concept and concept != "Kiến thức bài giảng":
            if is_correct:
                if concept in accumulated_weak_concepts:
                    accumulated_weak_concepts.remove(concept)
            else:
                if concept not in accumulated_weak_concepts:
                    accumulated_weak_concepts.append(concept)

    final_weak_concepts = accumulated_weak_concepts
    percentage = result.get("percentage", 0.0)
    learning_level = "Advanced" if percentage >= 80 else ("Intermediate" if percentage >= 60 else "Beginner")

    # Update StudentProgressAnalytics & mark status(N) = 'completed' (Unlocks N+1)
    db.update_student_session_progress(
        student_id=student_id,
        session_id=session_id,
        status="completed",
        score=result.get("total_score", 0.0),
        weak_concepts=final_weak_concepts,
        learning_level=learning_level
    )
    if transcript_id and transcript_id != session_id:
        db.update_student_session_progress(
            student_id=student_id,
            session_id=transcript_id,
            status="completed",
            score=result.get("total_score", 0.0),
            weak_concepts=final_weak_concepts,
            learning_level=learning_level
        )

    db.save_submission(result)

    return {
        "status": "success",
        "message": f"Chúc mừng bạn đã hoàn thành {session_id}! Buổi học tiếp theo đã được mở khóa.",
        "grading_result": result,
        "student_progress": {
            "session_id": session_id,
            "status": "completed",
            "weak_concepts": final_weak_concepts,
            "learning_level": learning_level
        }
    }


@app.get("/api/student/progress")
def get_student_progress(student_id: str = "2012345"):
    """GET /api/student/progress: Lấy bản đồ tiến độ & trạng thái mở khóa của sinh viên."""
    all_modules = db.get_all_modules()
    progress_map = []

    for idx, mod in enumerate(all_modules):
        mod_id = mod["module_id"]
        prog = db.get_student_session_progress(student_id, mod_id)

        if idx == 0:
            status = prog.get("status", "unlocked")
        else:
            prev_mod_id = all_modules[idx - 1]["module_id"]
            prev_prog = db.get_student_session_progress(student_id, prev_mod_id)
            if prev_prog.get("status") == "completed":
                status = prog.get("status", "unlocked")
                if status == "locked":
                    status = "unlocked"
            else:
                status = "locked"

        if prog.get("status") == "completed":
            status = "completed"

        # Check if student already has a generated quiz for this module
        quiz_key = f"{student_id}_{mod_id}"
        has_quiz = (db.get_quiz(quiz_key) is not None) or (db.get_quiz(mod_id) is not None)

        progress_map.append({
            "module_id": mod_id,
            "title": mod["title"],
            "session": mod["session"],
            "status": status,
            "score": prog.get("score", 0.0),
            "weak_concepts": prog.get("weak_concepts", []),
            "has_generated_quiz": has_quiz
        })

    return {"student_id": student_id, "progress": progress_map}


# Compatibility routes
@app.post("/api/generate-quiz")
def generate_quiz_legacy(payload: Dict[str, Any] = Body(...)):
    session = payload.get("session", "Day01")
    return student_generate_quiz(session, payload)

@app.post("/api/ai-tutor")
def ai_tutor(payload: Dict[str, Any] = Body(...)):
    selected_option = payload.get("selectedOption", "a")
    user_prompt = payload.get("userPrompt", "")
    return {
        "feedback": f"Phản hồi AI Tutor cho lựa chọn {selected_option.upper()}",
        "reference": "Slide Reference & Vector DB",
        "formula": "Rule: Grounding & Retrieval",
        "explanation": f"{user_prompt or 'AI Tutor đang giải thích chi tiết dựa trên tài liệu bài giảng.'}"
    }

@app.get("/api/v1/modules")
def get_modules():
    return {"modules": db.get_all_modules()}

@app.post("/api/v1/save-module")
def save_module(payload: Dict[str, Any] = Body(...)):
    return teacher_materials(payload)

@app.get("/api/v1/quiz/{quiz_id}")
def get_quiz_by_id(quiz_id: str):
    return get_student_session_quiz(quiz_id)
