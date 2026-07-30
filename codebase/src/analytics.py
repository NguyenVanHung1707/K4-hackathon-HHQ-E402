from typing import List, Dict, Any

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


class KnowledgeAnalytics:
    """Tổng hợp kết quả chấm bài của lớp và tạo Báo cáo bản đồ lỗ hổng kiến thức."""

    def __init__(self):
        self.settings = get_settings()

    def generate_class_report(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tạo báo cáo chi tiết cho Giảng viên / TA."""
        if not submissions:
            return {"error": "Không có dữ liệu bài nộp nào."}

        total_students = len(submissions)
        total_score_sum = sum(s.get("total_score", 0.0) for s in submissions)
        avg_score = round(total_score_sum / total_students, 1)

        concept_stats = {}
        students_needing_support = []

        for sub in submissions:
            student_name = sub.get("student_name", "Unknown")
            student_id = sub.get("student_id", "")
            percentage = sub.get("percentage", 0.0)

            # Cảnh báo học viên có điểm < 60%
            if percentage < 60.0:
                students_needing_support.append({
                    "student_id": student_id,
                    "student_name": student_name,
                    "score": sub.get("total_score", 0.0),
                    "percentage": percentage,
                    "status": "Cần TA hỗ trợ 1-on-1"
                })

            for qr in sub.get("question_results", []):
                concept = qr.get("concept", "Khái niệm chung")
                score = qr.get("score", 0.0)
                max_score = qr.get("max_score", 1.0)

                if concept not in concept_stats:
                    concept_stats[concept] = {"total_correct": 0, "total_attempts": 0}

                concept_stats[concept]["total_attempts"] += 1
                if score >= (max_score * 0.7):
                    concept_stats[concept]["total_correct"] += 1

        # Phân tích bản đồ lỗ hổng kiến thức
        knowledge_gaps = []
        for concept, stat in concept_stats.items():
            correct_rate = round((stat["total_correct"] / stat["total_attempts"]) * 100, 1)
            severity = "Mức độ Hổng Cao (⚠️⚠️⚠️)" if correct_rate < 60.0 else (
                "Mức độ Hổng Vừa (⚠️)" if correct_rate < 80.0 else "Đạt yêu cầu (✅)"
            )
            recommendation = (
                f"Cần dành 10 phút đầu buổi tiếp theo để giảng lại chuyên sâu về {concept}."
                if correct_rate < 60.0 else "Nắm chắc kiến thức, giữ nguyên tiến độ."
            )
            knowledge_gaps.append({
                "concept": concept,
                "correct_rate": f"{correct_rate}%",
                "status": severity,
                "recommendation": recommendation
            })

        return {
            "summary": {
                "total_submissions": total_students,
                "class_average_score": f"{avg_score} / 10.0",
                "students_below_target": len(students_needing_support)
            },
            "knowledge_gaps_map": knowledge_gaps,
            "students_needing_attention": students_needing_support
        }
