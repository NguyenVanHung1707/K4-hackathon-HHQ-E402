from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    SHORT_ANSWER = "short_answer"


class Question(BaseModel):
    id: str = Field(..., description="Mã câu hỏi (ví dụ: Q1, Q2)")
    type: QuestionType = Field(..., description="Loại câu hỏi")
    question: str = Field(..., description="Nội dung câu hỏi")
    options: Optional[List[str]] = Field(default=None, description="Danh sách đáp án cho trắc nghiệm")
    correct_answer: str = Field(..., description="Đáp án chuẩn hoặc từ điền đúng")
    rubric_keywords: Optional[List[str]] = Field(default=None, description="Từ khóa chấm bài tự luận")
    sample_answer: Optional[str] = Field(default=None, description="Câu trả lời mẫu cho bài tự luận")
    citation: str = Field(..., description="Mã trích dẫn bài giảng [transcript_id:Lxx-Lyy]")
    concept: str = Field(..., description="Khái niệm / chủ đề kiến thức liên quan")


class QuizData(BaseModel):
    status: str = "success"
    transcript_id: str
    total_questions: int
    questions: List[Question]


class SubmissionPayload(BaseModel):
    student_id: str = Field(default="HV001", description="Mã số học viên")
    student_name: str = Field(default="Học viên VLearn", description="Tên học viên")
    transcript_id: str = Field(default="T-LECTURE-01", description="Mã bài giảng")
    answers: Dict[str, str] = Field(..., description="Dictionary chứa câu trả lời theo q_id")


class QuestionResult(BaseModel):
    question_id: str
    concept: str
    user_answer: str
    score: float
    max_score: float
    feedback: str
    citation: str


class StudentGradingResult(BaseModel):
    student_id: str
    student_name: str
    total_score: float
    max_score: float
    percentage: float
    question_results: List[QuestionResult]


class KnowledgeGap(BaseModel):
    concept: str
    correct_rate: str
    status: str
    recommendation: str


class StudentAttention(BaseModel):
    student_id: str
    student_name: str
    score: float
    percentage: float
    status: str


class AnalyticsReportSummary(BaseModel):
    total_submissions: int
    class_average_score: str
    students_below_target: int


class AnalyticsReportData(BaseModel):
    summary: AnalyticsReportSummary
    knowledge_gaps_map: List[KnowledgeGap]
    students_needing_attention: List[StudentAttention]
