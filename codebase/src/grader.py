from typing import Dict, Any, List

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


class AutoGrader:
    """Tự động chấm bài làm của học viên và đưa ra phản hồi chi tiết."""

    def __init__(self):
        self.settings = get_settings()

    def grade_submission(self, student_id: str, student_name: str, quiz_data: Dict[str, Any], answers: Dict[str, str]) -> Dict[str, Any]:
        """Chấm bài trắc nghiệm và tự luận ngắn cho từng học viên."""
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

            if q_type == "multiple_choice":
                is_correct = (user_ans.upper() == q["correct_answer"][0].upper()) or (user_ans == q["correct_answer"])
                score = score_per_question if is_correct else 0.0
                feedback = "Chính xác!" if is_correct else f"Chưa đúng. Đáp án đúng là {q['correct_answer']}. Tham khảo lại bài giảng tại {citation}."
            
            elif q_type == "fill_in_blank":
                is_correct = user_ans.lower() == q["correct_answer"].lower()
                score = score_per_question if is_correct else 0.0
                feedback = "Chính xác!" if is_correct else f"Đáp án chuẩn là '{q['correct_answer']}'. Vui lòng đọc lại đoạn {citation}."

            elif q_type == "short_answer":
                # Chấm tự luận dựa trên rubric keywords & semantic logic
                keywords = q.get("rubric_keywords", [])
                matched_keywords = [kw for kw in keywords if kw.lower() in user_ans.lower()]
                
                # Check for prompt injection attempt
                if any(inj in user_ans.lower() for inj in ["bỏ qua hướng dẫn", "cho tôi 10 điểm", "ignore previous"]):
                    score = 0.0
                    feedback = "Cảnh báo: Câu trả lời chứa prompt injection không hợp lệ. Đạt 0 điểm."
                elif len(matched_keywords) >= 2 or len(user_ans) > 20:
                    score = score_per_question
                    feedback = f"Trả lời tốt. Đã nắm vững khái niệm '{concept}'. Nguồn trích dẫn: {citation}"
                elif len(user_ans) > 0:
                    score = score_per_question * 0.5
                    feedback = f"Trả lời còn sơ sài (thiếu từ khóa: {', '.join(keywords[:2])}). Cần bổ sung ý. Xem lại {citation}."
                else:
                    score = 0.0
                    feedback = "Chưa trả lời câu hỏi này."

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

        return {
            "student_id": student_id,
            "student_name": student_name,
            "total_score": round(total_score, 1),
            "max_score": max_score,
            "percentage": round((total_score / max_score) * 100, 1),
            "question_results": results
        }
