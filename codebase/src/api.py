from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

try:
    from codebase.src.generator import QuizGenerator
    from codebase.src.grader import AutoGrader
    from codebase.src.analytics import KnowledgeAnalytics
    from codebase.src.vector_store import RAGVectorStore
    from codebase.src.denoiser import TranscriptDenoiser
    from codebase.src.db import SQLiteDatabase
except ImportError:
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
    existing_quiz = db.get_quiz(quiz_key) or db.get_quiz(session_id)

    if existing_quiz and existing_quiz.get("questions") and len(existing_quiz.get("questions")) > 0:
        return {
            "status": "success",
            "has_existing": True,
            "session_id": session_id,
            "student_id": student_id,
            "questions": existing_quiz.get("questions")
        }

    return {
        "status": "needs_setup",
        "has_existing": False,
        "session_id": session_id,
        "student_id": student_id,
        "questions": []
    }


@app.post("/api/student/session/{session_id}/generate-quiz")
def student_generate_quiz(session_id: str, payload: Dict[str, Any] = Body(default={})):
    """POST /api/student/session/{session_id}/generate-quiz: Gọi AI sinh đề bài cá nhân hóa thời gian thực."""
    student_id = payload.get("student_id", "2012345")
    num_questions = payload.get("num_questions") or 3
    quiz_types = payload.get("quiz_types") or "Trắc nghiệm, Điền từ, Tự luận"
    difficulty = payload.get("difficulty_level") or payload.get("difficulty") or "Cơ bản"
    type_counts = payload.get("type_counts")

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

    mod = db.get_module_by_id(session_id)
    retrieved_context = mod.get("description", "") if mod else "Nội dung bài giảng AI Vector DB"

    # Generate Quiz
    generated_quiz = generator.generate_student_triggered_quiz(
        current_session_name=mod.get("title", session_id) if mod else session_id,
        retrieved_context=retrieved_context,
        weak_concepts=weak_concepts,
        num_questions=int(num_questions),
        quiz_types=quiz_types,
        difficulty=difficulty,
        type_counts=type_counts
    )

    # Purge old quiz data for this student & session before saving newly generated quiz
    quiz_key = f"{student_id}_{session_id}"
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
