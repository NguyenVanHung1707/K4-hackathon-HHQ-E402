import os
import json
import sqlite3
from typing import List, Dict, Any, Optional

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


class SQLiteDatabase:
    """Cơ sở dữ liệu SQLite lưu trữ Quiz Bank, Bài nộp học viên và Analytics."""

    def __init__(self, db_path: Optional[str] = None):
        self.settings = get_settings()
        if not db_path:
            db_dir = os.path.join(self.settings.data_dir, "db")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "vlearn.db")

        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Khởi tạo các bảng cơ sở dữ liệu SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Bảng Ngân hàng Bài tập (Quiz Bank Table)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    quiz_id TEXT PRIMARY KEY,
                    transcript_id TEXT NOT NULL,
                    total_questions INTEGER NOT NULL,
                    quiz_data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Bảng Bài nộp của Học viên (Submissions Table)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    transcript_id TEXT NOT NULL,
                    total_score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    percentage REAL NOT NULL,
                    submission_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print(f"[SQLiteDatabase] Connected & Initialized SQLite DB at: {self.db_path}")

    def save_quiz(self, quiz_id: str, transcript_id: str, quiz_data: Dict[str, Any]):
        """Lưu bộ bài tập vào SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO quizzes (quiz_id, transcript_id, total_questions, quiz_data_json)
                VALUES (?, ?, ?, ?)
            """, (quiz_id, transcript_id, quiz_data.get("total_questions", 3), json.dumps(quiz_data, ensure_ascii=False)))
            conn.commit()

    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Lấy bộ bài tập từ SQLite theo ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quiz_data_json FROM quizzes WHERE quiz_id = ? OR transcript_id = ?", (quiz_id, quiz_id))
            row = cursor.fetchone()
            if row:
                return json.loads(row["quiz_data_json"])
        return None

    def save_submission(self, result: Dict[str, Any]):
        """Lưu kết quả chấm bài của học viên vào SQLite."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO submissions (student_id, student_name, transcript_id, total_score, max_score, percentage, submission_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                result.get("student_id", "HV001"),
                result.get("student_name", "Học viên VLearn"),
                result.get("transcript_id", "T-01"),
                result.get("total_score", 0.0),
                result.get("max_score", 10.0),
                result.get("percentage", 0.0),
                json.dumps(result, ensure_ascii=False)
            ))
            conn.commit()

    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ lịch sử bài nộp để tạo báo cáo Analytics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT submission_json FROM submissions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [json.loads(row["submission_json"]) for row in rows]
