# 💻 VLearn EduAI Prototype Codebase

Prototype hệ thống **Sinh bài tập tự động & Phân tích lỗ hổng kiến thức** dành cho khoá AI Thực Chiến (VLearn).

---

## 🛠️ Bảng Ma Trận Tính Năng Prototype (Prototype Matrix)

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| **Quiz Generator Agent** | **Working (Thật 100%)** | Gọi LLM/RAG phân tích transcript bài giảng, sinh bài tập trắc nghiệm, điền khuyết, tự luận ngắn kèm trích dẫn `[transcript_id:Lxx-Lyy]`. |
| **Auto Grader Agent** | **Working (Thật 100%)** | Chấm bài trắc nghiệm + tự luận ngắn dựa trên rubric keywords, ngữ nghĩa và phòng chống Prompt Injection gian lận. |
| **Knowledge Gap Analytics** | **Working (Thật 100%)** | Tổng hợp điểm số lớp học, xuất Báo cáo Bản đồ Lỗ hổng Kiến thức (Cao/Vừa/Đạt) & danh sách học viên cần hỗ trợ 1-on-1. |
| **LLM Denoising Engine** | **Working (Thật 100%)** | Lọc rác transcript bài giảng thô (chào hỏi, giải lao, hành chính). |
| **Vector DB & SQLite DB** | **Working (Thật 100%)** | ChromaDB cho RAG Vector Embeddings và SQLite DB cho Quiz Bank & Submissions. |
| **Next.js Web Frontend** | **Working (Thật 100%)** | Web Portal tại `frontend/` cho Học viên & Dashboard Giảng viên / TA. |

---

## ⚡ Hướng Dẫn Chạy Nhanh (Pip)

Xem hướng dẫn chi tiết toàn bộ các bước khởi chạy tại file **[RUNNING_GUIDE.md](../RUNNING_GUIDE.md)**.

```bash
# 1. Cài đặt các thư viện Python:
pip install -r codebase/requirements.txt

# 2. Chạy CLI Demo (Test luồng nhanh):
python codebase/src/main.py

# 3. Chạy Evaluation Suite (20 cases):
python eval/run_eval.py

# 4. Khởi chạy REST API Server:
python codebase/src/main.py --server

# 5. Khởi chạy Next.js Web Frontend:
cd frontend && npm run dev
```
