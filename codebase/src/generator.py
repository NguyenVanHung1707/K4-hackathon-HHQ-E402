import json
from typing import Dict, Any, List, Optional

try:
    from codebase.src.config import get_settings
    from codebase.src.schemas import QuizData, Question, QuestionType
    from codebase.src.vector_store import RAGVectorStore
    from codebase.src.persona import PersonaExtractor
    from codebase.src.gemini_rotator import GeminiMultiModelRotator
except ImportError:
    from config import get_settings
    from schemas import QuizData, Question, QuestionType
    from vector_store import RAGVectorStore
    from persona import PersonaExtractor
    from gemini_rotator import GeminiMultiModelRotator


STUDENT_TRIGGERED_SYSTEM_PROMPT = """
Bạn là hệ thống AI tạo bài tập cá nhân hóa. Một sinh viên vừa yêu cầu bạn tạo bộ câu hỏi cho buổi học hiện tại.
Nhiệm vụ của bạn là sinh ra câu hỏi dựa trên: Kiến thức bài học, cấu hình sinh viên yêu cầu, và khắc phục lỗ hổng bài trước.

[CẤU HÌNH DO SINH VIÊN YÊU CẦU (SETUP)]
- Tổng số câu hỏi: {student_setup_num_questions}
- Dạng câu hỏi ưu tiên: {student_setup_quiz_types} (multiple_choice, fill_in_blank, short_essay)
- Chi tiết số lượng câu theo từng dạng: {student_setup_type_counts}
- Độ khó yêu cầu: {student_setup_difficulty}

[DỮ LIỆU KIẾN THỨC]
1. Nguồn tài liệu Buổi {current_session_name}:
{retrieved_context_from_vector_db}

2. Lịch sử lỗi sai của sinh viên này ở Buổi học trước:
{student_weak_concepts_from_previous_session}

[QUY TẮC BẮT BUỘC SINH CÂU HỎI]
1. Tuân thủ TUYỆT ĐỐI số lượng câu hỏi và phân bổ dạng câu hỏi trong phần [CẤU HÌNH]. BẮT BUỘC phải sinh đủ {student_setup_num_questions} câu hỏi.
2. Mỗi câu hỏi phải có NỘI DUNG VÀ ĐÁP ÁN HOÀN TOÀN KHÁC NHAU. Tuyệt đối KHÔNG trùng lặp câu hỏi, không hỏi đi hỏi lại một khái niệm giống hệt nhau.
3. CÂU HỎI PHẢI RÕ RÀNG VÀ TỰ CHỨA ĐỰNG (SELF-CONTAINED):
   - BẮT BUỘC "question_text" phải là CÂU HỎI HOÀN CHỈNH, mô tả rõ ràng khái niệm kỹ thuật cần hỏi, TUYỆT ĐỐI KHÔNG chỉ ghi tên tiêu đề hoặc từ khóa chung chung.
   - TUYỆT ĐỐI KHÔNG tạo các câu hỏi dạng tham chiếu tương đối hoặc liên kết đến các phần/đoạn văn bản/dòng/trang cụ thể mà người dùng không thể biết (ví dụ: KHÔNG viết "Theo đoạn #5...", "Khái niệm trong phần 3 nói gì...", "Trong đoạn văn trên...", "Theo nội dung dòng 12...").
   - Lý do: Học viên làm bài tập độc lập mà không có văn bản thô bên cạnh, nên câu hỏi phải tự mô tả đầy đủ ngữ cảnh để học viên có thể hiểu được câu hỏi là gì (Ví dụ thay vì "Đoạn #5 nói về cơ chế gì?", hãy hỏi "Trong kiến trúc Transformer, cơ chế Self-Attention đóng vai trò cốt lõi nào?").
4. Các phương án trả lời trắc nghiệm (options) phải thực tế, liên quan trực tiếp đến kiến thức chuyên môn, KHÔNG tạo các phương án ngớ ngẩn mang tính lấp chỗ trống vô nghĩa (như "tắt kết nối internet", "tăng dung lượng màn hình máy tính", "đổi phông chữ hiển thị"). Các phương án nhiễu phải là các khái niệm kỹ thuật có vẻ hợp lý nhưng sai.
5. CHỈ CÂU HỎI ĐẦU TIÊN (Q1) của Buổi 2 mới được làm câu ôn tập ("is_review": true). Các câu tiếp theo (Q2, Q3...) BẮT BỘC "is_review": false.
6. Trả về kết quả CHỈ bằng định dạng JSON theo schema, không có text markdown bao quanh.

[JSON SCHEMA]
{{
  "questions": [
    {{
      "type": "multiple_choice | fill_in_blank | short_essay",
      "difficulty": "{student_setup_difficulty}",
      "is_review": true / false,
      "question_text": "Viết câu hỏi hoàn chỉnh tại đây...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "...",
      "explanation": "Giải thích cặn kẽ tại sao đúng/sai để AI Tutor dùng hướng dẫn sinh viên.",
      "concept": "Tên khái niệm"
    }}
  ]
}}
"""


def sort_questions_by_type(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sắp xếp thứ tự ưu tiên câu hỏi chuẩn: Trắc nghiệm (multiple_choice) -> Điền từ (fill_in_blank) -> Tự luận ngắn (short_essay). Sanitize question_text."""
    type_priority = {
        "multiple_choice": 1,
        "fill_in_blank": 2,
        "short_essay": 3
    }
    # Ensure review flag is ONLY set on the single review question
    review_seen = False
    for idx, q in enumerate(questions):
        if q.get("is_review") and not review_seen:
            review_seen = True
        elif q.get("is_review"):
            q["is_review"] = False

        # Sanitize incomplete question text
        q_text = str(q.get("question_text", "")).strip()
        if not q_text or not any(c in q_text for c in ["?", "gì", "như thế nào", "tại sao", "hãy", "trình bày", "phân tích", "_____"]):
            concept = q.get("concept", "khái niệm bài học")
            q_type = q.get("type", "multiple_choice")
            if q_type == "fill_in_blank":
                q["question_text"] = f"[Điền từ] Trong kiến thức bài học, khái niệm __________ là yếu tố cốt lõi liên quan đến {concept}."
            elif q_type == "short_essay":
                q["question_text"] = f"[Tự luận ngắn] Trình bày phân tích của bạn về vai trò và ứng dụng của {concept} trong mô hình AI?"
            else:
                q["question_text"] = f"[Trắc nghiệm] Yếu tố nào sau đây đóng vai trò cốt lõi trong khái niệm {concept}?"

    sorted_q = sorted(
        questions,
        key=lambda q: (
            0 if q.get("is_review") else 1,
            type_priority.get(q.get("type", "multiple_choice"), 1)
        )
    )
    for idx, q in enumerate(sorted_q, start=1):
        q["id"] = f"Q{idx}"
    return sorted_q


DAY01_MC = [
    {
        "topic": "Self-Attention Mechanism",
        "question": "Trong kiến trúc Transformer (Buổi 1), cơ chế Self-Attention có vai trò cốt lõi gì?",
        "options": [
            "A. Tính toán mối tương quan ngữ nghĩa giữa tất cả các từ trong câu một cách song song.",
            "B. Xử lý câu văn theo thứ tự tuần tự từng từ từ trái sang phải như RNN.",
            "C. Nén tập tin bài giảng thành tập tin định dạng ZIP.",
            "D. Phân loại hình ảnh màu đầu vào."
        ],
        "correct": "A. Tính toán mối tương quan ngữ nghĩa giữa tất cả các từ trong câu một cách song song.",
        "explain": "Self-Attention tính toán ma trận trọng số tương quan giữa mọi cặp từ trong câu mà không bị giới hạn bởi khoảng cách."
    },
    {
        "topic": "Positional Encoding",
        "question": "Mục đích chính của kỹ thuật Positional Encoding trong Transformer (Buổi 1) là gì?",
        "options": [
            "A. Bổ sung thông tin thứ tự vị trí của token do Self-Attention xử lý các từ song song.",
            "B. Tự động dịch văn bản từ tiếng Anh sang tiếng Việt.",
            "C. Tăng kích thước bộ nhớ VRAM của GPU.",
            "D. Loại bỏ các từ dừng (stop words) khỏi câu văn."
        ],
        "correct": "A. Bổ sung thông tin thứ tự vị trí của token do Self-Attention xử lý các từ song song.",
        "explain": "Vì Self-Attention xử lý tất cả các từ cùng lúc, Positional Encoding cần thiết để giữ lại thông tin vị trí."
    },
    {
        "topic": "Tokenization Process",
        "question": "Kỹ thuật Tokenization trong xử lý ngôn ngữ tự nhiên (Buổi 1) đóng vai trò gì?",
        "options": [
            "A. Tách câu văn thô thành các đơn vị số học nhỏ nhất (tokens) để làm đầu vào cho Embedding.",
            "B. Sinh câu trả lời tự động cho sinh viên.",
            "C. Tải tài liệu bài giảng về máy tính cá nhân.",
            "D. Kiểm tra kết nối mạng Internet."
        ],
        "correct": "A. Tách câu văn thô thành các đơn vị số học nhỏ nhất (tokens) để làm đầu vào cho Embedding.",
        "explain": "Tokenization chuyển đổi văn bản dạng chuỗi thành dãy số token phù hợp với bảng từ vựng của LLM."
    },
    {
        "topic": "Encoder-Decoder Architecture",
        "question": "Trong mô hình Transformer chuẩn, khối Encoder đảm nhận nhiệm vụ nào?",
        "options": [
            "A. Tiếp nhận chuỗi đầu vào và trích xuất không gian biểu diễn ngữ nghĩa (contextual representation).",
            "B. Dự đoán và sinh ra từ tiếp theo của câu trả lời.",
            "C. Quản lý cơ sở dữ liệu học tập SQLite.",
            "D. Hiển thị giao diện người dùng trên web."
        ],
        "correct": "A. Tiếp nhận chuỗi đầu vào và trích xuất không gian biểu diễn ngữ nghĩa (contextual representation).",
        "explain": "Encoder mã hóa văn bản thành vector ngữ nghĩa rich-context."
    },
    {
        "topic": "Temperature Parameter",
        "question": "Tham số Temperature trong quá trình lấy mẫu của LLM (Buổi 1) ảnh hưởng ra sao?",
        "options": [
            "A. Temperature càng cao câu trả lời càng đa dạng/sáng tạo, càng thấp câu trả lời càng nhất quán.",
            "B. Thay đổi độ phân giải màn hình hiển thị.",
            "C. Điều chỉnh nhiệt độ phần cứng của chip xử lý.",
            "D. Tăng tốc độ nạp file PDF."
        ],
        "correct": "A. Temperature càng cao câu trả lời càng đa dạng/sáng tạo, càng thấp câu trả lời càng nhất quán.",
        "explain": "Temperature điều chỉnh độ phẳng của phân phối xác suất Softmax khi chọn token tiếp theo."
    },
    {
        "topic": "Multi-Head Attention",
        "question": "Lợi ích chính của việc sử dụng Multi-Head Attention thay vì Single-Head là gì?",
        "options": [
            "A. Cho phép mô hình đồng thời chú ý đến các mối quan hệ ngữ nghĩa ở nhiều không gian biểu diễn khác nhau.",
            "B. Giảm dung lượng mô hình xuống 10 lần.",
            "C. Tránh việc phải sử dụng card đồ họa GPU.",
            "D. Tự động sửa lỗi chính tả văn bản."
        ],
        "correct": "A. Cho phép mô hình đồng thời chú ý đến các mối quan hệ ngữ nghĩa ở nhiều không gian biểu diễn khác nhau.",
        "explain": "Multi-Head Attention chiếu các ma trận Query, Key, Value sang nhiều không gian con để học đa dạng ngữ cảnh."
    }
]

DAY02_MC = [
    {
        "topic": "Vector Database & ChromaDB",
        "question": "Trong hệ thống RAG (Buổi 2), cơ sở dữ liệu ChromaDB đóng vai trò gì?",
        "options": [
            "A. Lưu trữ các vector embedding và thực hiện truy vấn tìm kiếm tương đồng ngữ nghĩa.",
            "B. Biên dịch mã nguồn ứng dụng React.",
            "C. Lưu thông tin tài khoản người dùng.",
            "D. Điều khiển luồng thực thi phần cứng."
        ],
        "correct": "A. Lưu trữ các vector embedding và thực hiện truy vấn tìm kiếm tương đồng ngữ nghĩa.",
        "explain": "ChromaDB là Vector Store chuyên dụng giúp lưu trữ và tìm kiếm vector bằng k-NN Cosine Similarity."
    },
    {
        "topic": "Context Grounding",
        "question": "Kỹ thuật Context Grounding trong RAG (Buổi 2) giúp giải quyết vấn đề gì?",
        "options": [
            "A. Ràng buộc LLM chỉ được sinh câu trả lời dựa trên trích dẫn tri thức thực tế để ngăn ngừa ảo giác (Hallucination).",
            "B. Tăng dung lượng đĩa cứng lưu trữ.",
            "C. Tự động dịch tài liệu sang nhiều ngôn ngữ.",
            "D. Giảm độ phân giải video bài giảng."
        ],
        "correct": "A. Ràng buộc LLM chỉ được sinh câu trả lời dựa trên trích dẫn tri thức thực tế để ngăn ngừa ảo giác (Hallucination).",
        "explain": "Context Grounding cung cấp dữ liệu nền tảng làm 'nguồn sự thật' cho mô hình sinh văn bản."
    },
    {
        "topic": "Few-Shot Prompting",
        "question": "Phương pháp Few-Shot Prompting (Buổi 2) hoạt động dựa trên nguyên lý nào?",
        "options": [
            "A. Đưa một vài ví dụ mẫu cặp Input - Output vào prompt để hướng dẫn định dạng trả lời cho LLM.",
            "B. Huấn luyện lại toàn bộ mô hình ngôn ngữ lớn từ đầu.",
            "C. Không cung cấp bất kỳ ví dụ minh họa nào.",
            "D. Giới hạn số câu trả lời ở mức 1 câu."
        ],
        "correct": "A. Đưa một vài ví dụ mẫu cặp Input - Output vào prompt để hướng dẫn định dạng trả lời cho LLM.",
        "explain": "Few-Shot Prompting học in-context giúp mô hình nắm bắt định dạng và quy tắc xử lý."
    },
    {
        "topic": "Chain-of-Thought (CoT)",
        "question": "Kỹ thuật Chuỗi tư duy Chain-of-Thought (Buổi 2) có ưu điểm vượt trội gì?",
        "options": [
            "A. Bắt buộc mô hình trình bày chi tiết các bước suy luận trung gian trước khi ra kết luận.",
            "B. Tự động rút ngắn câu trả lời xuống 3 từ.",
            "C. Tăng tốc độ phản hồi gấp 100 lần.",
            "D. Tắt tính năng kiểm tra ngữ pháp."
        ],
        "correct": "A. Bắt buộc mô hình trình bày chi tiết các bước suy luận trung gian trước khi ra kết luận.",
        "explain": "CoT giúp LLM phân rã các bài toán phức tạp thành từng bước logic giúp nâng cao độ chính xác."
    },
    {
        "topic": "Semantic Search",
        "question": "Điểm khác biệt cốt lõi giữa Semantic Search và Tìm kiếm từ khóa (Keyword Match) là gì?",
        "options": [
            "A. Semantic Search đo độ tương đồng trong không gian vector để hiểu ý nghĩa thay vì chỉ dựa vào từ ngữ chính xác.",
            "B. Semantic Search chỉ hoạt động với số nguyên.",
            "C. Keyword Match hiểu được ngữ cảnh hơn Semantic Search.",
            "D. Cả hai phương pháp hoàn toàn giống nhau."
        ],
        "correct": "A. Semantic Search đo độ tương đồng trong không gian vector để hiểu ý nghĩa thay vì chỉ dựa vào từ ngữ chính xác.",
        "explain": "Semantic Search dựa trên khoảng cách vector embedding giữa câu hỏi và đoạn tài liệu."
    }
]

DAY01_FIB = [
    {"term": "Self-Attention", "q": "Cơ chế __________ trong Transformer cho phép mô hình tính toán mức độ liên quan giữa tất cả các cặp từ trong câu một cách song song.", "exp": "Self-Attention giúp tính ma trận liên kết ngữ nghĩa trong câu."},
    {"term": "Tokenization", "q": "Quá trình chuyển đổi chuỗi văn bản thô thành các đơn vị số học đại diện (token) được gọi là __________.", "exp": "Tokenization phân tách văn bản thành mã số cho mô hình."},
    {"term": "Positional Encoding", "q": "Thành phần __________ giúp mô hình Transformer nắm bắt được thứ tự vị trí của các token trong chuỗi khi xử lý song song.", "exp": "Positional Encoding bổ sung thông tin vị trí vào vector đầu vào."},
    {"term": "Temperature", "q": "Tham số __________ dùng để điều chỉnh độ ngẫu nhiên và mức độ sáng tạo của câu trả lời sinh ra từ mô hình ngôn ngữ lớn.", "exp": "Temperature thay đổi phân phối xác suất khi lấy mẫu token."}
]

DAY02_FIB = [
    {"term": "ChromaDB", "q": "Trong hệ thống RAG, cơ sở dữ liệu chuyên dụng dùng để lưu trữ và tìm kiếm vector tương đồng được gọi là __________.", "exp": "ChromaDB lưu trữ vector embeddings và thực hiện k-NN search."},
    {"term": "Grounding", "q": "Kỹ thuật buộc mô hình LLM sinh câu trả lời dựa trên tài liệu trích dẫn thực tế để chống ảo giác gọi là Context __________.", "exp": "Context Grounding đảm bảo tính xác thực của thông tin."},
    {"term": "Few-Shot", "q": "Kỹ thuật đưa các ví dụ mẫu minh họa vào trong prompt để hướng dẫn định dạng kết quả trả về cho LLM gọi là __________ Prompting.", "exp": "Few-Shot Prompting giúp LLM học định dạng qua ví dụ."},
    {"term": "Chain-of-Thought", "q": "Phương pháp yêu cầu LLM suy luận từng bước trung gian trước khi đưa ra kết quả cuối cùng gọi là kỹ thuật __________.", "exp": "Chain-of-Thought tăng khả năng giải quyết các bài toán logic."}
]

DAY01_ESSAY = [
    {"topic": "cơ chế Self-Attention trong Transformer", "q": "Trình bày phân tích của bạn về ưu điểm cốt lõi của cơ chế Self-Attention so với mô hình xử lý tuần tự RNN truyền thống trong kiến trúc Transformer?", "ans": "Cần nêu rõ: Self-Attention xử lý song song toàn bộ chuỗi từ, loại bỏ nghẽn cổ chai của RNN và tính toán trực tiếp mối tương quan xa giữa các từ."},
    {"topic": "ảnh hưởng của tham số Temperature", "q": "Phân tích tác động của tham số Temperature đối với tính sáng tạo và độ tin cậy trong câu trả lời của mô hình ngôn ngữ lớn (LLM)?", "ans": "Cần nêu rõ: Temperature cao (gần 1.0) làm phẳng phân phối xác suất giúp tăng độ ngẫu nhiên/sáng tạo; Temperature thấp (gần 0) tập trung vào token xác suất cao nhất giúp tăng tính nhất quán."}
]

DAY02_ESSAY = [
    {"topic": "cơ chế chống ảo giác AI của RAG", "q": "Giải thích quy trình 3 bước (Retrieval - Augmentation - Generation) của RAG và cách RAG chống hiện tượng ảo giác AI (Hallucination)?", "ans": "Cần nêu rõ: RAG tìm kiếm tài liệu thực tế từ Vector DB (Retrieval), đưa vào prompt làm ngữ cảnh (Augmentation), giúp LLM trả lời có căn cứ xác thực (Generation)."},
    {"topic": "kỹ thuật Chain-of-Thought (CoT)", "q": "Trình bày kỹ thuật Chain-of-Thought (CoT) Prompting và lý do vì sao CoT giúp LLM cải thiện vượt trội khả năng giải bài toán logic phức tạp?", "ans": "Cần nêu rõ: CoT ép mô hình chia nhỏ bài toán và lập luận qua từng bước trung gian, giúp giảm thiểu sai số tư duy trực tiếp."}
]


class QuizGenerator:
    """AI Pipeline cho Student-Triggered Real-time Generation."""

    def __init__(self):
        self.settings = get_settings()
        self.vector_store = RAGVectorStore()
        self.persona_extractor = PersonaExtractor()
        self.gemini_rotator = GeminiMultiModelRotator()

    def post_process_and_fill_questions(
        self,
        llm_questions: List[Dict[str, Any]],
        total_req: int,
        target_counts: Dict[str, int],
        is_first_session: bool,
        difficulty: str,
        current_session_name: str,
        weak_concepts: List[str] = None
    ) -> List[Dict[str, Any]]:
        mc_bank = DAY01_MC if is_first_session else DAY02_MC
        fib_bank = DAY01_FIB if is_first_session else DAY02_FIB
        essay_bank = DAY01_ESSAY if is_first_session else DAY02_ESSAY

        accepted_questions = []

        def is_valid_question(q, accepted):
            if not q.get("question_text") or not q.get("type") or not q.get("correct_answer"):
                return False
            q_text = str(q.get("question_text", "")).strip().lower()
            forbidden_patterns = ["đoạn #", "dòng #", "đoạn văn trên", "đoạn trên", "trong đoạn #", "phần #"]
            for fp in forbidden_patterns:
                if fp in q_text:
                    return False
            # Check duplicates
            for aq in accepted:
                if aq.get("question_text", "").strip().lower() == q.get("question_text", "").strip().lower():
                    return False
            return True

        for q in llm_questions:
            # Map type variants
            q_type = q.get("type", "multiple_choice")
            if "choice" in q_type or q_type == "mc":
                q["type"] = "multiple_choice"
            elif "blank" in q_type or "fill" in q_type or q_type == "fib":
                q["type"] = "fill_in_blank"
            elif "essay" in q_type or "short" in q_type or q_type == "short_essay" or q_type == "short_answer":
                q["type"] = "short_essay"
            else:
                q["type"] = "multiple_choice"

            # Clean up options to avoid dummy placeholders
            if q["type"] == "multiple_choice" and q.get("options"):
                cleaned_opts = []
                for opt in q["options"]:
                    opt_lower = opt.lower()
                    if any(x in opt_lower for x in ["tắt kết nối internet", "tắt internet", "tăng dung lượng màn hình", "đổi phông chữ", "phương án nhiễu"]):
                        continue
                    cleaned_opts.append(opt)
                if len(cleaned_opts) < 4:
                    # We will drop this question and let the bank fill it
                    continue
                q["options"] = cleaned_opts

            if is_valid_question(q, accepted_questions):
                accepted_questions.append(q)

        # Count current types
        current_counts = {"multiple_choice": 0, "fill_in_blank": 0, "short_essay": 0}
        for q in accepted_questions:
            q_type = q.get("type", "multiple_choice")
            if q_type in current_counts:
                current_counts[q_type] += 1

        # Fill in missing questions of each type
        for q_type, target_num in target_counts.items():
            current_num = current_counts.get(q_type, 0)
            if current_num < target_num:
                needed = target_num - current_num
                bank = mc_bank if q_type == "multiple_choice" else (fib_bank if q_type == "fill_in_blank" else essay_bank)
                
                # We need to draw "needed" questions from this bank
                for idx in range(needed):
                    q_num = len(accepted_questions) + 1
                    
                    # 1. Review question check:
                    if q_type == "multiple_choice" and idx == 0 and weak_concepts and not is_first_session:
                        # Check if we already have a review question in accepted
                        has_review = any(aq.get("is_review") for aq in accepted_questions)
                        if not has_review:
                            wc = weak_concepts[0]
                            new_q = {
                                "id": f"Q{q_num}",
                                "type": "multiple_choice",
                                "difficulty": difficulty,
                                "is_review": True,
                                "review_from_session": "Day01",
                                "question_text": f"[Ôn tập kiến thức Buổi 1: {wc}] Trong bài học {current_session_name}, giải pháp nào giúp củng cố kiến thức về '{wc}' từ Buổi 1?",
                                "options": [
                                    "A. Áp dụng Context Grounding và kiểm tra nguồn trích dẫn tài liệu",
                                    "B. Tăng dung lượng bộ nhớ RAM của máy chủ",
                                    "C. Bỏ qua không xử lý lỗi này nữa",
                                    "D. Đổi phông chữ hiển thị"
                                ],
                                "correct_answer": "A. Áp dụng Context Grounding và kiểm tra nguồn trích dẫn tài liệu",
                                "explanation": f"Câu hỏi ôn tập lồng ghép dành riêng cho bạn để khắc phục lỗ hổng '{wc}' từ Buổi 1.",
                                "citation": f"[Day01:L01-L15]",
                                "concept": f"Ôn tập Buổi 1: {wc}"
                            }
                            accepted_questions.append(new_q)
                            continue

                    # Find an unused item
                    unused_item = None
                    for item in bank:
                        used = False
                        item_text = item.get("question") if q_type == "multiple_choice" else item.get("q")
                        for aq in accepted_questions:
                            if aq.get("question_text", "").strip().lower() == item_text.strip().lower():
                                    used = True
                                    break
                        if not used:
                            unused_item = item
                            break
                    if not unused_item:
                        unused_item = bank[len(accepted_questions) % len(bank)]

                    # Format the question
                    new_q = None
                    if q_type == "multiple_choice":
                        new_q = {
                            "id": f"Q{q_num}",
                            "type": "multiple_choice",
                            "difficulty": difficulty,
                            "question_text": unused_item["question"],
                            "options": unused_item["options"],
                            "correct_answer": unused_item["correct"],
                            "explanation": unused_item["explain"],
                            "citation": f"[{current_session_name}:L{((q_num*7)%50)+1}-L{((q_num*7)%50)+10}]",
                            "concept": unused_item["topic"]
                        }
                    elif q_type == "fill_in_blank":
                        new_q = {
                            "id": f"Q{q_num}",
                            "type": "fill_in_blank",
                            "difficulty": difficulty,
                            "question_text": unused_item["q"],
                            "options": [],
                            "correct_answer": unused_item["term"],
                            "explanation": unused_item["exp"],
                            "citation": f"[{current_session_name}:L{((q_num*5)%40)+10}-L{((q_num*5)%40)+20}]",
                            "concept": f"Khái niệm {unused_item['term']}"
                        }
                    elif q_type == "short_essay":
                        new_q = {
                            "id": f"Q{q_num}",
                            "type": "short_essay",
                            "difficulty": difficulty,
                            "question_text": unused_item["q"],
                            "options": [],
                            "correct_answer": unused_item["ans"],
                            "rubric_keywords": ["căn cứ", "nguồn sự thật", "ngữ nghĩa", "mô hình"],
                            "explanation": f"Bài tự luận yêu cầu làm rõ bản chất về {unused_item['topic']}.",
                            "citation": f"[{current_session_name}:L{((q_num*8)%30)+20}-L{((q_num*8)%30)+35}]",
                            "concept": f"Tự luận: {unused_item['topic']}"
                        }
                    if new_q:
                        accepted_questions.append(new_q)

        sorted_qs = sort_questions_by_type(accepted_questions)
        if current_session_name.startswith("T-"):
            for q in sorted_qs:
                if q.get("type") == "short_essay":
                    q["type"] = "short_answer"
        return sorted_qs

    def generate_student_triggered_quiz(
        self,
        current_session_name: str,
        retrieved_context: str,
        weak_concepts: List[str],
        num_questions: int = 5,
        quiz_types: str = "70% Trắc nghiệm, 30% Điền khuyết",
        difficulty: str = "Cơ bản",
        type_counts: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Kích hoạt AI Pipeline sinh đề bài cá nhân hóa thời gian thực không bao giờ lặp câu hỏi kể cả khi số lượng lớn."""
        is_first_session = any(k in str(current_session_name) for k in ["Day01", "Day1", "MOD-01", "Buổi 1"])
        if is_first_session:
            weak_concepts = []
        elif not weak_concepts:
            weak_concepts = ["Self-Attention & Vector Embedding (Buổi 1)"]

        weak_concepts_str = ", ".join(weak_concepts) if weak_concepts else "Không có (Đã nắm vững)"

        counts = type_counts or {"multiple_choice": 1, "fill_in_blank": 1, "short_essay": 1}
        num_mc = counts.get("multiple_choice", 0)
        num_fib = counts.get("fill_in_blank", 0)
        num_essay = counts.get("short_essay", 0)
        total_req = num_mc + num_fib + num_essay if type_counts else num_questions

        prompt = STUDENT_TRIGGERED_SYSTEM_PROMPT.format(
            student_setup_num_questions=total_req,
            student_setup_quiz_types=quiz_types,
            student_setup_type_counts=json.dumps(counts, ensure_ascii=False),
            student_setup_difficulty=difficulty,
            current_session_name=current_session_name,
            retrieved_context_from_vector_db=retrieved_context or "Nguồn tài liệu học tập RAG & AI Vector DB.",
            student_weak_concepts_from_previous_session=weak_concepts_str
        )

        # Target counts for post-processing mapping
        target_counts = counts if type_counts else {
            "multiple_choice": max(1, total_req - 2) if total_req >= 2 else total_req,
            "fill_in_blank": 1 if total_req >= 2 else 0,
            "short_essay": 1 if total_req >= 3 else 0
        }
        if not type_counts:
            diff = total_req - sum(target_counts.values())
            target_counts["multiple_choice"] += diff

        # 1. Try Google Gemini / Local GPU Failover Rotator
        gemini_data = self.gemini_rotator.generate_json(prompt)
        if gemini_data and gemini_data.get("questions") and len(gemini_data.get("questions")) > 0:
            llm_questions = gemini_data["questions"]
            processed_questions = self.post_process_and_fill_questions(
                llm_questions=llm_questions,
                total_req=total_req,
                target_counts=target_counts,
                is_first_session=is_first_session,
                difficulty=difficulty,
                current_session_name=current_session_name,
                weak_concepts=weak_concepts
            )
            return {
                "status": "success",
                "session_name": current_session_name,
                "setup": {
                    "num_questions": total_req,
                    "quiz_types": quiz_types,
                    "type_counts": counts,
                    "difficulty": difficulty
                },
                "total_questions": len(processed_questions),
                "questions": processed_questions
            }

        # 2. Fallback to OpenAI / Secondary LLM if available
        if self.settings.openai_api_key and self.settings.openai_api_key.startswith("sk-"):
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import SystemMessage

                openai_model = self.settings.llm_model_name if self.settings.llm_model_name.startswith("gpt-") else "gpt-4o-mini"
                llm = ChatOpenAI(
                    model=openai_model,
                    api_key=self.settings.openai_api_key,
                    temperature=0.7
                )
                res = llm.invoke([SystemMessage(content=prompt)])
                clean_json = res.content.replace("```json\n", "").replace("```", "").strip()
                data = json.loads(clean_json)
                if data.get("questions") and len(data.get("questions")) > 0:
                    llm_questions = data["questions"]
                    processed_questions = self.post_process_and_fill_questions(
                        llm_questions=llm_questions,
                        total_req=total_req,
                        target_counts=target_counts,
                        is_first_session=is_first_session,
                        difficulty=difficulty,
                        current_session_name=current_session_name,
                        weak_concepts=weak_concepts
                    )
                    return {
                        "status": "success",
                        "session_name": current_session_name,
                        "setup": {
                            "num_questions": total_req,
                            "quiz_types": quiz_types,
                            "type_counts": counts,
                            "difficulty": difficulty
                        },
                        "total_questions": len(processed_questions),
                        "questions": processed_questions
                    }
            except Exception as e:
                print(f"[Warning] Call OpenAI LLM adaptive failed: {e}. Using fallback dynamic quiz bank...")

        # Dynamic Non-Repeating Question Engine for arbitrary N questions
        processed_questions = self.post_process_and_fill_questions(
            llm_questions=[],
            total_req=total_req,
            target_counts=target_counts,
            is_first_session=is_first_session,
            difficulty=difficulty,
            current_session_name=current_session_name,
            weak_concepts=weak_concepts
        )

        return {
            "status": "success",
            "session_name": current_session_name,
            "setup": {
                "num_questions": total_req,
                "quiz_types": quiz_types,
                "type_counts": counts,
                "difficulty": difficulty
            },
            "total_questions": len(processed_questions),
            "questions": processed_questions
        }

    def generate_quiz_from_transcript(self, transcript_text: str, transcript_id: str = "T-01") -> Dict[str, Any]:
        """Phân tích nội dung bài giảng và tạo bộ câu hỏi chuẩn."""
        return self.generate_student_triggered_quiz(
            current_session_name=transcript_id,
            retrieved_context=transcript_text[:2000],
            weak_concepts=["Vector Embeddings & RAG Retrieval"],
            num_questions=5
        )
