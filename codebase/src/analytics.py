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
        """Tạo báo cáo chi tiết cho Giảng viên / TA với phân loại bài học & lỗ hổng kiến thức."""
        if not submissions:
            return {
                "summary": {
                    "total_submissions": 0,
                    "class_average_score": "0.0 / 10.0",
                    "students_below_target": 0
                },
                "knowledge_gaps_map": [],
                "student_reports": []
            }

        total_score_sum = 0.0
        concept_stats = {}

        # Dùng map để gộp bài nộp mới nhất của từng sinh viên cho từng buổi học (student_id + transcript_id)
        latest_submissions_map: Dict[str, Dict[str, Any]] = {}

        for sub in submissions:
            student_id = sub.get("student_id", "2012345")
            session_id = sub.get("transcript_id") or sub.get("session_id") or "Day01"
            key = f"{student_id}_{session_id}"

            # Giữ bài nộp gần nhất hoặc điểm tốt nhất
            if key not in latest_submissions_map:
                latest_submissions_map[key] = sub

        unique_subs = list(latest_submissions_map.values())
        total_students = len(unique_subs)

        student_reports = []
        students_needing_support_count = 0

        for sub in unique_subs:
            student_name = sub.get("student_name", "Nguyen Van A")
            student_id = sub.get("student_id", "2012345")
            session_id = sub.get("transcript_id") or sub.get("session_id") or "Day01"
            total_score = round(sub.get("total_score", 0.0), 1)
            percentage = sub.get("percentage", round((total_score / 10.0) * 100, 1))

            total_score_sum += total_score

            # Tìm danh sách các câu làm sai / yếu để liệt kê lỗ hổng kiến thức
            weak_concepts = []
            for qr in sub.get("question_results", []):
                concept = qr.get("concept", "Kiến thức bài giảng")
                score = qr.get("score", 0.0)
                max_score = qr.get("max_score", 1.0)

                # Thống kê tổng hợp cả lớp
                if concept not in concept_stats:
                    concept_stats[concept] = {"total_correct": 0, "total_attempts": 0}

                concept_stats[concept]["total_attempts"] += 1
                if score >= (max_score * 0.7):
                    concept_stats[concept]["total_correct"] += 1
                else:
                    if concept not in weak_concepts:
                        weak_concepts.append(concept)

            status = "On Track"
            if percentage < 60.0:
                status = "At Risk"
                students_needing_support_count += 1
            elif percentage < 80.0:
                status = "Needs Review"

            student_reports.append({
                "student_id": student_id,
                "student_name": student_name,
                "session_id": session_id,
                "session_title": f"Buổi {session_id.replace('Day', '')}" if "Day" in session_id else session_id,
                "score": total_score,
                "percentage": percentage,
                "status": status,
                "weak_concepts": weak_concepts if weak_concepts else ["Nắm vững bài học"]
            })

        avg_score = round(total_score_sum / max(1, total_students), 1)

        # Phân tích bản đồ lỗ hổng kiến thức cả lớp (Radar chart)
        knowledge_gaps = []
        for concept, stat in concept_stats.items():
            correct_rate = round((stat["total_correct"] / max(1, stat["total_attempts"])) * 100, 1)
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
                "students_below_target": students_needing_support_count
            },
            "knowledge_gaps_map": knowledge_gaps,
            "student_reports": student_reports,
            "students_needing_attention": student_reports
        }
