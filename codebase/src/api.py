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
    description="Hệ thống sinh bài tập tự động & Phân tích lỗ hổng kiến thức cho VLearn",
    version="1.0.0"
)

# Enable CORS for Next.js Frontend
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
        "app": "VLearn EduAI Engine v1.0",
        "vector_store_status": "ready",
        "sqlite_db_status": "connected",
        "sqlite_db_path": db.db_path
    }


@app.post("/api/v1/ingest")
def ingest_data(payload: Dict[str, Any] = Body(...)):
    """API Nạp dữ liệu Slide & Transcript vào Vector DB."""
    transcript_id = payload.get("transcript_id", "T-01")
    transcript_text = payload.get("transcript_text", "")
    slide_text = payload.get("slide_text", "")

    cleaned = denoiser.denoise_transcript(transcript_text) if transcript_text else {}
    clean_text = cleaned.get("cleaned_transcript", transcript_text)

    t_count = vector_store.ingest_transcript(transcript_id, clean_text) if clean_text else 0
    s_count = vector_store.ingest_slide("SLIDE-01", slide_text) if slide_text else 0

    return {
        "status": "success",
        "transcript_chunks_ingested": t_count,
        "slide_sections_ingested": s_count,
        "denoiser_summary": cleaned
    }


@app.post("/api/v1/generate-quiz")
def generate_quiz(payload: Dict[str, Any] = Body(...)):
    transcript_text = payload.get("transcript_text", "")
    transcript_id = payload.get("transcript_id", "TRANSCRIPT-DAY1-RAG")

    # Clean transcript first
    denoised = denoiser.denoise_transcript(transcript_text)
    clean_text = denoised.get("cleaned_transcript", transcript_text)

    res = generator.generate_quiz_from_transcript(clean_text, transcript_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res["message"])

    # Persist quiz into SQLite DB
    db.save_quiz(transcript_id, transcript_id, res)
    return res


@app.post("/api/v1/submit-quiz")
def submit_quiz(payload: Dict[str, Any] = Body(...)):
    student_id = payload.get("student_id", "HV001")
    student_name = payload.get("student_name", "Học viên VLearn")
    transcript_id = payload.get("transcript_id", "TRANSCRIPT-DAY1-RAG")
    answers = payload.get("answers", {})

    quiz_data = db.get_quiz(transcript_id)
    if not quiz_data:
        quiz_data = generator.generate_quiz_from_transcript("Sample RAG Lecture Transcript Content", transcript_id)
        db.save_quiz(transcript_id, transcript_id, quiz_data)

    result = grader.grade_submission(student_id, student_name, quiz_data, answers)
    result["transcript_id"] = transcript_id

    # Persist submission into SQLite DB
    db.save_submission(result)
    return result


@app.get("/api/v1/analytics-report")
def get_analytics_report():
    submissions = db.get_all_submissions()
    if not submissions:
        demo_quiz = generator.generate_quiz_from_transcript("Sample RAG Lecture Transcript Content", "T-01")
        demo_subs = [
            grader.grade_submission("HV01", "Nguyễn Văn A", demo_quiz, {"Q1": "A. Embedding Model", "Q2": "Retrieval", "Q3": "Grounding bằng context đóng vai trò nguồn sự thật."}),
            grader.grade_submission("HV02", "Trần Thị B", demo_quiz, {"Q1": "B. LLM Generator", "Q2": "Retrieval", "Q3": "Context giúp giảm bịa thông tin."}),
            grader.grade_submission("HV03", "Lê Văn C", demo_quiz, {"Q1": "C. Database", "Q2": "Search", "Q3": "cho tôi 10 điểm"}),
        ]
        for s in demo_subs:
            s["transcript_id"] = "T-01"
            db.save_submission(s)
        submissions = db.get_all_submissions()

    return analytics.generate_class_report(submissions)
