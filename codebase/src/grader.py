from typing import Dict, Any, List

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


class AutoGrader:
    """Tự động chấm bài trắc nghiệm, điền khuyết và tự luận ngắn (phòng chống Prompt Injection)."""

    INJECTION_TERMS = [
        "bỏ qua hướng dẫn", "cho tôi 10 điểm", "ignore previous instructions",
        "ignore instructions", "system prompt override", "cho 10 diem",
        "override score", "gán cho tôi điểm tối đa"
    ]

    def __init__(self):
        self.settings = get_settings()

    def grade_submission(self, student_id: str, student_name: str, quiz_data: Dict[str, Any], answers: Dict[str, str]) -> Dict[str, Any]:
        """Chấm điểm bài làm chi tiết cho từng học viên."""
        total_score = 0.0
        max_score = 10.0
        results = []
        questions = quiz_data.get("questions", [])

        if not questions:
            return {"error": "Không tìm thấy dữ liệu bộ câu hỏi."}

        score_per_question = max_score / len(questions)

        for q in questions:
            q_id = q["id"]
            user_ans = answers.get(q_id, "").strip()
            q_type = q["type"]
            concept = q.get("concept", "Kiến thức chung")
            citation = q.get("citation", "")

            # 1. Trắc nghiệm (Multiple Choice)
            if q_type == "multiple_choice":
                correct_opt = q["correct_answer"].strip()
                is_correct = (user_ans.upper() == correct_opt[0].upper()) or (user_ans.lower() == correct_opt.lower())
                score = score_per_question if is_correct else 0.0
                feedback = "Chính xác!" if is_correct else f"Chưa chính xác. Đáp án đúng là {correct_opt}. Tham khảo lại bài giảng tại {citation}."

            # 2. Điền khuyết (Fill in Blank)
            elif q_type == "fill_in_blank":
                correct_val = q["correct_answer"].strip().lower()
                is_correct = user_ans.lower() == correct_val
                score = score_per_question if is_correct else 0.0
                feedback = "Chính xác!" if is_correct else f"Chưa đúng. Đáp án chuẩn là '{q['correct_answer']}'. Đọc lại đoạn {citation}."

            # 3. Tự luận ngắn (Short Answer)
            elif q_type == "short_answer":
                # Check for Prompt Injection Attack
                user_ans_lower = user_ans.lower()
                if any(term in user_ans_lower for term in self.INJECTION_TERMS):
                    score = 0.0
                    feedback = "🔴 CẢNH BÁO: Phát hiện hành vi Prompt Injection / Gian lận. Bài làm bị tính 0 điểm."
                else:
                    keywords = q.get("rubric_keywords", ["nguồn sự thật", "grounding", "context"]) or ["nguồn sự thật", "context"]
                    matched = [kw for kw in keywords if kw.lower() in user_ans_lower]

                    if len(matched) >= 2 or len(user_ans) >= 25:
                        score = score_per_question
                        feedback = f"Trả lời xuất sắc! Đã nắm vững khái niệm '{concept}'. Trích dẫn bài giảng: {citation}"
                    elif len(user_ans) > 0:
                        score = round(score_per_question * 0.5, 2)
                        feedback = f"Trả lời tương đối tốt nhưng còn sơ sài (thiếu ý: {', '.join(keywords[:2])}). Xem lại {citation}."
                    else:
                        score = 0.0
                        feedback = "Bỏ trống câu hỏi này."

            total_score += score
            results.append({
                "question_id": q_id,
                "concept": concept,
                "user_answer": user_ans,
                "score": round(score, 2),
                "max_score": round(score_per_question, 2),
                "feedback": feedback,
                "citation": citation
            })

        final_percentage = round((total_score / max_score) * 100, 1)

        return {
            "student_id": student_id,
            "student_name": student_name,
            "total_score": round(total_score, 1),
            "max_score": max_score,
            "percentage": final_percentage,
            "question_results": results
        }
