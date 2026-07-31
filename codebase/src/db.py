import os
import sqlite3
import json
from typing import Dict, Any, List, Optional

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


def scan_day_directories(data_dir: str) -> List[Dict[str, Any]]:
    """Tự động quét chỉ các thư mục có định dạng DayXX (ví dụ: Day01, Day02) trong data/."""
    modules = []
    if not os.path.exists(data_dir):
        return modules

    items = sorted(os.listdir(data_dir))
    for item in items:
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith("Day"):
            day_num = item.replace("Day", "").strip()
            modules.append({
                "module_id": item,
                "title": f"Buổi {day_num} ({item})",
                "session": f"Session {item}: Học liệu nguyên bản & bài tập AI",
                "description": f"Chỉ quét học liệu từ thư mục {item} trong data/."
            })
    return modules


class SQLiteDatabase:
    """Quản lý lưu trữ SQLite Persistence cho VLearn Platform."""

    def __init__(self):
        self.settings = get_settings()
        self.db_path = os.path.join(self.settings.data_dir, "db", "vlearn.db")

        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Khởi tạo cấu trúc schema cơ sở dữ liệu vlearn.db."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Bảng Quizzes: Lưu trữ bộ đề do AI sinh ra
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    quiz_id TEXT PRIMARY KEY,
                    transcript_id TEXT NOT NULL,
                    total_questions INTEGER DEFAULT 5,
                    quiz_data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Bảng Submissions: Lưu trữ bài làm & kết quả chấm chi tiết
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    transcript_id TEXT NOT NULL,
                    total_score REAL NOT NULL,
                    max_score REAL DEFAULT 10.0,
                    percentage REAL DEFAULT 0.0,
                    submission_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Bảng Modules: Lưu danh sách bài học
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS modules (
                    module_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    session TEXT NOT NULL,
                    description TEXT,
                    questions_json TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Bảng StudentProgressAnalytics: Lưu tiến độ & weak_concepts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_progress (
                    student_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    status TEXT DEFAULT 'locked',
                    score REAL DEFAULT 0.0,
                    weak_concepts_json TEXT DEFAULT '[]',
                    learning_level TEXT DEFAULT 'Intermediate',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (student_id, session_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS question_banks (
                    bank_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    questions_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def save_quiz(self, quiz_id: str, transcript_id: str, quiz_data: Dict[str, Any]):
        """Lưu bộ bài tập mới vào SQLite (Ghi đè hoàn toàn dữ liệu cũ)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO quizzes (quiz_id, transcript_id, total_questions, quiz_data_json, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (quiz_id, transcript_id, quiz_data.get("total_questions", 3), json.dumps(quiz_data, ensure_ascii=False)))
            conn.commit()

    def delete_quiz(self, quiz_id: str):
        """Xóa hoàn toàn dữ liệu bộ câu hỏi cũ trong SQLite khi sinh viên chọn tạo lại đề mới."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quizzes WHERE quiz_id = ? OR transcript_id = ?", (quiz_id, quiz_id))
            conn.commit()

    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Lấy bộ bài tập từ SQLite theo ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quiz_data_json FROM quizzes WHERE quiz_id = ? OR transcript_id = ? ORDER BY created_at DESC", (quiz_id, quiz_id))
            row = cursor.fetchone()
            if row:
                return json.loads(row["quiz_data_json"])
        return None

    def save_question_bank(self, session_id: str, difficulty: str, questions: List[Dict[str, Any]]):
        bank_id = f"{session_id}_{difficulty}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO question_banks (bank_id, session_id, difficulty, questions_json, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (bank_id, session_id, difficulty, json.dumps(questions, ensure_ascii=False)))
            conn.commit()

    def get_question_bank(self, session_id: str, difficulty: str) -> List[Dict[str, Any]]:
        bank_id = f"{session_id}_{difficulty}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT questions_json
                FROM question_banks
                WHERE bank_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (bank_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["questions_json"])
        return []

    def save_submission(self, result: Dict[str, Any]):
        """Lưu / Ghi đè log bài nộp mới nhất của học viên vào SQLite cho buổi học tương ứng."""
        student_id = result.get("student_id", "2012345")
        transcript_id = result.get("transcript_id", "Day01")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Ghi đè log cũ của sinh viên tại buổi học này để tạo log mới nhất
            cursor.execute("DELETE FROM submissions WHERE student_id = ? AND transcript_id = ?", (student_id, transcript_id))
            cursor.execute("""
                INSERT INTO submissions (student_id, student_name, transcript_id, total_score, max_score, percentage, submission_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                student_id,
                result.get("student_name", "Học viên VLearn"),
                transcript_id,
                result.get("total_score", 0.0),
                result.get("max_score", 10.0),
                result.get("percentage", 0.0),
                json.dumps(result, ensure_ascii=False)
            ))
            conn.commit()

    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ lịch sử bài nộp mới nhất để tạo báo cáo Analytics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT submission_json FROM submissions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [json.loads(row["submission_json"]) for row in rows]

    def save_module(self, module_id: str, title: str, session: str, description: str, questions: List[Dict[str, Any]]):
        """Lưu Module bài học do Giảng viên phát hành vào SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO modules (module_id, title, session, description, questions_json)
                VALUES (?, ?, ?, ?, ?)
            """, (module_id, title, session, description, json.dumps(questions, ensure_ascii=False)))
            conn.commit()

    def get_all_modules(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các Module bài học. Chỉ quét và nạp các thư mục DayXX trong data/."""
        day_mods = scan_day_directories(self.settings.data_dir)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for m in day_mods:
                cursor.execute("""
                    INSERT OR REPLACE INTO modules (module_id, title, session, description, questions_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (m["module_id"], m["title"], m["session"], m["description"], "[]"))
            conn.commit()

            cursor.execute("SELECT module_id, title, session, description, questions_json, created_at FROM modules WHERE module_id LIKE 'Day%' ORDER BY module_id ASC")
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append({
                    "module_id": row["module_id"],
                    "title": row["title"],
                    "session": row["session"],
                    "description": row["description"],
                    "questions": json.loads(row["questions_json"]),
                    "created_at": row["created_at"]
                })
            return results

    def get_module_by_id(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin Module bài học theo ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT module_id, title, session, description, questions_json, created_at FROM modules WHERE module_id = ?", (module_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "module_id": row["module_id"],
                    "title": row["title"],
                    "session": row["session"],
                    "description": row["description"],
                    "questions": json.loads(row["questions_json"]),
                    "created_at": row["created_at"]
                }
        return None

    def get_student_session_progress(self, student_id: str, session_id: str) -> Dict[str, Any]:
        """Lấy trạng thái tiến độ học tập của sinh viên tại buổi session_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, score, weak_concepts_json, learning_level FROM student_progress WHERE student_id = ? AND session_id = ?", (student_id, session_id))
            row = cursor.fetchone()
            if row:
                return {
                    "student_id": student_id,
                    "session_id": session_id,
                    "status": row["status"],
                    "score": row["score"],
                    "weak_concepts": json.loads(row["weak_concepts_json"]),
                    "learning_level": row["learning_level"]
                }
            default_status = "unlocked" if session_id in ["Day01", "Day1", "MOD-01"] else "locked"
            return {
                "student_id": student_id,
                "session_id": session_id,
                "status": default_status,
                "score": 0.0,
                "weak_concepts": [],
                "learning_level": "Intermediate"
            }

    def update_student_session_progress(self, student_id: str, session_id: str, status: str, score: float, weak_concepts: List[str], learning_level: str = "Intermediate"):
        """Cập nhật tiến độ và danh sách weak_concepts mới nhất cho sinh viên khi hoàn thành/làm lại buổi học."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO student_progress (student_id, session_id, status, score, weak_concepts_json, learning_level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(student_id, session_id) DO UPDATE SET
                    status = excluded.status,
                    score = excluded.score,
                    weak_concepts_json = excluded.weak_concepts_json,
                    learning_level = excluded.learning_level,
                    updated_at = CURRENT_TIMESTAMP
            """, (student_id, session_id, status, score, json.dumps(weak_concepts, ensure_ascii=False), learning_level))
            conn.commit()

    def get_previous_session_weakness(self, student_id: str, previous_session_id: str) -> Dict[str, Any]:
        """Truy vấn lỗ hổng kiến thức (weak_concepts) từ buổi học N-1."""
        progress = self.get_student_session_progress(student_id, previous_session_id)
        return {
            "student_id": student_id,
            "session_id": previous_session_id,
            "weak_concepts": progress.get("weak_concepts", [])
        }

    def get_previous_wrong_questions(self, student_id: str, previous_session_id: str) -> List[Dict[str, Any]]:
        """Return questions the student got wrong in the previous session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT submission_json
                FROM submissions
                WHERE student_id = ? AND transcript_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (student_id, previous_session_id))
            row = cursor.fetchone()

        if not row:
            return []

        submission = json.loads(row["submission_json"])
        quiz_data = self.get_quiz(f"{student_id}_{previous_session_id}") or self.get_quiz(previous_session_id) or {}
        question_map = {}
        for idx, question in enumerate(quiz_data.get("questions", [])):
            q_id = str(question.get("id") or f"Q{idx + 1}")
            question_map[q_id] = question

        wrong_questions = []
        for qr in submission.get("question_results", []):
            max_score = float(qr.get("max_score") or 1.0)
            score = float(qr.get("score") or 0.0)
            if score >= max_score * 0.7:
                continue

            source_question = question_map.get(str(qr.get("question_id")), {})
            question_text = qr.get("question_text") or source_question.get("question_text") or source_question.get("question") or qr.get("feedback", "")
            if not question_text:
                continue

            wrong_questions.append({
                "source_session_id": previous_session_id,
                "question_id": qr.get("question_id"),
                "question_text": question_text,
                "type": qr.get("question_type") or source_question.get("type", "multiple_choice"),
                "concept": qr.get("concept") or source_question.get("concept", "Kien thuc bai truoc"),
                "options": qr.get("options") or source_question.get("options", []),
                "correct_answer": qr.get("correct_answer") or source_question.get("correct_answer", ""),
                "explanation": qr.get("explanation") or source_question.get("explanation") or qr.get("feedback", ""),
                "citation": qr.get("citation") or source_question.get("citation", previous_session_id)
            })

        return wrong_questions
