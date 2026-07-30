# 💻 VLearn EduAI Prototype Codebase

Prototype hệ thống **Sinh bài tập tự động & Phân tích lỗ hổng kiến thức** dành cho khoá AI Thực Chiến (VLearn).

---

## 🛠️ Trạng thái Prototype (Prototype Matrix)

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| **Quiz Generator** | **Working (Thật)** | Gọi LLM phân tích transcript bài giảng, sinh bài tập trắc nghiệm, điền khuyết, tự luận ngắn kèm trích dẫn `[transcript_id:line]`. |
| **Auto Grader** | **Working (Thật)** | Tự động chấm bài trắc nghiệm + bài tự luận ngắn của học viên dựa trên đáp án chuẩn và lý giải chi tiết. |
| **Knowledge Gap Analytics** | **Working (Thật)** | Phân tích tỉ lệ trả lời đúng/sai của lớp, xuất biểu đồ/báo cáo bản đồ lỗ hổng kiến thức. |
| **Giao diện LMS** | **Mock** | Giả lập luồng nhận bài làm qua RESTful API / CLI. |

---

## ⚡ Hướng dẫn Chạy Prototype

```bash
# 1. Di chuyển vào thư mục codebase
cd codebase

# 2. Tạo virtualenv và cài đặt dependencies
python -m venv .venv
source .venv/bin/activate  # Hoặc .venv\Scripts\Activate.ps1 trên Windows
pip install -r requirements.txt

# 3. Tạo file .env và điền OPENAI_API_KEY
cp .env.example .env

# 4. Khởi chạy CLI Demo hoặc API Server
python src/main.py --demo      # Chạy thử nghiệm luồng từ sinh bài tập -> chấm bài -> báo cáo
python src/main.py --server    # Chạy Web API Server tại http://localhost:8000
```
