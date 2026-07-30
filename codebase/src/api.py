from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any, List

try:
    from codebase.src.generator import QuizGenerator
    from codebase.src.grader import AutoGrader
    from codebase.src.analytics import KnowledgeAnalytics
except ImportError:
    from generator import QuizGenerator
    from grader import AutoGrader
    from analytics import KnowledgeAnalytics

app = FastAPI(
    title="VLearn EduAI API Engine",
    description="Hệ thống sinh bài tập tự động & Phân tích lỗ hổng kiến thức cho VLearn",
    version="1.0.0"
)

generator = QuizGenerator()
grader = AutoGrader()
analytics = KnowledgeAnalytics()

DB_QUIZZES = {}
DB_SUBMISSIONS = []


@app.get("/")
def read_root():
    return {"status": "ok", "app": "VLearn EduAI Engine v1.0"}


@app.post("/api/v1/generate-quiz")
def generate_quiz(payload: Dict[str, Any] = Body(...)):
    transcript_text = payload.get("transcript_text", "")
    transcript_id = payload.get("transcript_id", "T-LECTURE-01")

    res = generator.generate_quiz_from_transcript(transcript_text, transcript_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res["message"])

    DB_QUIZZES[transcript_id] = res
    return res


@app.post("/api/v1/submit-quiz")
def submit_quiz(payload: Dict[str, Any] = Body(...)):
    student_id = payload.get("student_id", "HV001")
    student_name = payload.get("student_name", "Học viên VLearn")
    transcript_id = payload.get("transcript_id", "T-LECTURE-01")
    answers = payload.get("answers", {})

    quiz_data = DB_QUIZZES.get(transcript_id)
    if not quiz_data:
        quiz_data = generator.generate_quiz_from_transcript("Sample RAG Lecture Transcript Content", transcript_id)

    result = grader.grade_submission(student_id, student_name, quiz_data, answers)
    DB_SUBMISSIONS.append(result)
    return result


@app.get("/api/v1/analytics-report")
def get_analytics_report():
    if not DB_SUBMISSIONS:
        demo_subs = [
            grader.grade_submission("HV01", "Nguyễn Văn A", generator.generate_quiz_from_transcript("text", "T-01"), {"Q1": "A. Embedding Model", "Q2": "Retrieval", "Q3": "Grounding bằng context"}),
            grader.grade_submission("HV02", "Trần Thị B", generator.generate_quiz_from_transcript("text", "T-01"), {"Q1": "B. LLM Generator", "Q2": "Retrieval", "Q3": "Context giúp hạn chế hallucination"}),
            grader.grade_submission("HV03", "Lê Văn C", generator.generate_quiz_from_transcript("text", "T-01"), {"Q1": "C. Database", "Q2": "Search", "Q3": "Không biết"}),
        ]
        return analytics.generate_class_report(demo_subs)

    return analytics.generate_class_report(DB_SUBMISSIONS)
