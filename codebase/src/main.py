import sys
import os
import json

# Add current directory and root to sys.path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Fix Windows console encoding if needed
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from codebase.src.generator import QuizGenerator
    from codebase.src.grader import AutoGrader
    from codebase.src.analytics import KnowledgeAnalytics
except ImportError:
    from generator import QuizGenerator
    from grader import AutoGrader
    from analytics import KnowledgeAnalytics


def run_cli_demo():
    print("=" * 70)
    print("DEMO LAT CAT: VLearn EduAI - Sinh Bai Tap & Bao Cao Lo Hong Kien Thuc")
    print("=" * 70)

    sample_transcript = """
    Hôm nay chúng ta học bài RAG (Retrieval-Augmented Generation).
    Trong kiến trúc RAG, thành phần Embedding Model chịu trách nhiệm chuyển đổi các đoạn văn bản thành vector số.
    Quá trình trích xuất các đoạn văn bản có độ tương đồng cao nhất từ Vector Database gọi là quá trình Retrieval.
    Việc cung cấp Context cho LLM đóng vai trò như nguồn sự thật (Grounding), giúp ngăn chặn hiện tượng Hallucination.
    """

    print("\n[Buoc 1] Giang vien dan Transcript Bai 3 -> AI Phan tich & Sinh Bai Tap...")
    generator = QuizGenerator()
    quiz = generator.generate_quiz_from_transcript(sample_transcript, transcript_id="TRANSCRIPT-DAY3-RAG")
    
    print(f"[OK] Da sinh thanh cong {quiz['total_questions']} cau hoi kem trich dan:")
    for idx, q in enumerate(quiz['questions'], 1):
        print(f"  {idx}. [{q['type'].upper()}] {q['question']}")
        print(f"     -> Trich dan: {q['citation']}")

    print("\n[Buoc 2] Mo phong 3 Hoc vien nop bai lam...")
    grader = AutoGrader()
    
    sub1 = grader.grade_submission(
        student_id="HV001",
        student_name="Nguyen Van A",
        quiz_data=quiz,
        answers={
            "Q1": "A. Embedding Model",
            "Q2": "Retrieval",
            "Q3": "Context đóng vai trò làm nguồn sự thật (Grounding) giúp LLM không bị hallucination khi trả lời."
        }
    )
    print(f"  * Hoc vien HV001 (Nguyen Van A): {sub1['total_score']}/{sub1['max_score']} diem ({sub1['percentage']}%)")

    sub2 = grader.grade_submission(
        student_id="HV002",
        student_name="Tran Thi B",
        quiz_data=quiz,
        answers={
            "Q1": "B. LLM Generator", # Sai câu 1
            "Q2": "Retrieval",
            "Q3": "Vì Context cung cấp dữ liệu chuẩn nên không bị bịa."
        }
    )
    print(f"  * Hoc vien HV002 (Tran Thi B): {sub2['total_score']}/{sub2['max_score']} diem ({sub2['percentage']}%)")

    sub3 = grader.grade_submission(
        student_id="HV003",
        student_name="Le Van C (Hoc yeu)",
        quiz_data=quiz,
        answers={
            "Q1": "C. SQLite Database", # Sai câu 1
            "Q2": "Search",              # Sai câu 2
            "Q3": "Em chưa hiểu phần này lắm." # Sai câu 3
        }
    )
    print(f"  * Hoc vien HV003 (Le Van C): {sub3['total_score']}/{sub3['max_score']} diem ({sub3['percentage']}%)")

    print("\n[Buoc 3] Xuat Bao Cao Lo Hong Kien Thuc Cho Giang Vien & TA...")
    analytics = KnowledgeAnalytics()
    report = analytics.generate_class_report([sub1, sub2, sub3])

    print("\nBAO CAO LO HONG KIEN THUC CA LOP:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        print("Starting FastAPI Server...")
        import uvicorn
        uvicorn.run("codebase.src.api:app", host="0.0.0.0", port=8000, reload=True)
    else:
        run_cli_demo()
