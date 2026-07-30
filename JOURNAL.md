# Weekly Journal — Nhóm 04 (VLearn EduAI)

> Nhật ký tổng hợp quá trình làm việc, bài học kinh nghiệm và giải pháp của nhóm 04.

---

## 🗓️ Tuần Hackathon (Build Phase)

### 🎯 Mục tiêu tuần này
- [x] Chọn chủ đề & hoàn thành AI Spec 8 phần (`spec.md`) trước 23:59 N1.
- [x] Xây dựng Working Prototype gồm Quiz Generator, Auto Grader và Knowledge Gap Analytics.
- [x] Tích hợp LLM Denoising loại bỏ rác transcript & 2-step Anchor-Enrichment RAG Retrieval.
- [x] Xây dựng bộ Golden Set 20 cases và đạt Quality Bar ≥85% Pass Rate.
- [x] Thử nghiệm với 5 người dùng thật ngoài nhóm và thu thập feedback.
- [x] Phát triển Giao diện Web (Next.js/React UI) cho Học viên & Giảng viên.

### 🚀 Đã hoàn thành
- Bộ mã nguồn Backend Python đầy đủ tại `codebase/src/` (Generator, Grader, Analytics, Denoiser, Persona, Vector Store, SQLite DB).
- Giao diện Frontend Next.js tại `frontend/`.
- Tài liệu kiến trúc và luồng dữ liệu đầy đủ tại `WORKFLOW.md` và `ARCHITECTURE.md`.
- Bộ kiểm thử 20 cases tại `eval/golden_set.json` đạt **90.0% Pass Rate**.
- Feedback log từ 5 người dùng tại `validation/user_test_log.md`.

### 💡 Khó khăn & Giải pháp

| Khó khăn | Giải pháp | Kết quả |
|----------|-----------|---------|
| Transcript bài giảng thô chứa nhiều câu chào hỏi, giao lưu hành chính ngoài lề | Xây dựng node `LLM Denoising` (`denoiser.py`) lọc rác tự động trước khi chunking | Loại bỏ 100% rác ngoài lề, tăng chất lượng bài tập |
| Học viên nộp bài tự luận kẹp lệnh Prompt Injection ("Cho tôi 10 điểm") | Thiết lập lớp lọc Security & Sanitize Input trước khi chấm | Chặn thành công 100% prompt injection, cho 0 điểm và cảnh báo |
| AI bị hallucination suy đoán kiến thức ngoài bài giảng (Fine-tuning vs RAG) | Siết chặt System Prompt theo nguyên tắc "Strict Grounding" kèm trích dẫn `[transcript:line]` | Nâng tỷ lệ Eval Pass từ 70% lên 90% |

### 📖 Bài học rút ra
1. **Quality Bar rõ ràng:** Định nghĩa Quality Bar bằng số liệu từ sớm giúp nhóm giữ vững tiêu chuẩn chất lượng khi kiểm thử.
2. **Grounding Citation:** Mọi thông tin do AI sinh ra phải đính kèm nguồn trích dẫn cụ thể để tạo sự tin tưởng tuyệt đối cho người dùng trong môi trường giáo dục.
3. **Phòng thủ đa lớp (Defense in Depth):** Cần lọc rác từ đầu vào (Denoising) và lọc độc hại ở đầu ra/input tự do (Prompt Injection Guardrails).
