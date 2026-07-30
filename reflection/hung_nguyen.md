# 🪞 Reflection Cá Nhân — Nguyễn Văn Hùng (Trưởng Nhóm)

- **Vai trò trong nhóm:** Trưởng nhóm & AI Engineer phụ trách Kiến trúc AI Spec, Thiết kế Prompt & LangGraph Generator Agent (`codebase/src/generator.py`).
- **Phần công việc đảm nhận:** 
  1. Xây dựng tài liệu `spec.md` (8 phần + Changelog).
  2. Phát triển Generator Engine phân tích transcript bài giảng và sinh 3 dạng bài tập (trắc nghiệm, điền khuyết, tự luận ngắn) có đính kèm trích dẫn `[transcript_id:line]`.
  3. Phối hợp thiết kế bộ 20 test cases cho Golden Set (`eval/golden_set.json`).

- **AI hỗ trợ như thế nào trong quá trình build:**
  - Sử dụng Claude Code & Antigravity IDE để tự động hoá việc tạo mẫu Pydantic Schemas, viết unit test mock data, và tối ưu hóa System Prompt chống hallucination.
  - Sử dụng AI để rà soát 4 lớp chỗ khó (ERR-1.1 đến ERR-4.2) và xây dựng bộ lọc Prompt Injection.

- **Bài học rút ra từ một case fail của nhóm:**
  - *Case Fail:* Ở lượt chạy Eval 1, hệ thống rớt 3 case do AI tự động suy đoán thêm kiến thức về *Fine-tuning* trong khi bài giảng transcript chỉ dạy về *RAG cơ bản* (lỗi ERR-1.1 - Grounding Failure).
  - *Bài học:* Không được để LLM suy luận tự do mà phải siết chặt System Prompt với nguyên tắc "Strict Grounding": Chỉ được đặt câu hỏi trên dữ liệu transcript có sẵn, nếu không có phải từ chối hoặc bỏ qua. Điều này giúp tăng tỷ lệ Eval Pass từ 70% lên 90% ở lượt chạy thứ 2.
