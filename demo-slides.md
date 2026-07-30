# 🎤 Slide Trình Bày Demo — VLearn EduAI (6 Trang)

---

## Slide 1: Bằng Chứng Pain & Vấn Đề (Problem & Evidence)
- **Tên dự án:** VLearn EduAI — Sinh Bài Tập Tự Động & Phân Tích Lỗ Hổng Kiến Thức.
- **Pain cụ thể:** Giảng viên/TA tốn 2.5 giờ/buổi để soạn và chấm bài tập. 70% buổi học thiếu dữ liệu đo lường mức độ hiểu bài tức thì của người học.
- **Bằng chứng:**
  - Khảo sát 24 người: **83.3%** xác nhận gặp vướng mắc.
  - Phân tích chatlog VLearn: **34.2%** câu hỏi học viên hỏi lại kiến thức cũ ngay sau buổi học.

---

## Slide 2: Quyết Định Chọn & Lát Cắt Một Câu (Impact & Slice)
- **Bảng so sánh impact:** Chọn giải pháp sinh bài tập tự động từ transcript + báo cáo lỗ hổng (tiết kiệm **15 giờ/tuần** cho TA).
- **Lát cắt MỘT CÂU:**  
  > *"Giảng viên đưa transcript bài giảng -> AI phân tích nội dung để tự động sinh 5 câu bài tập (trắc nghiệm, điền khuyết, tự luận) kèm đáp án & trích dẫn -> Học viên nộp bài -> AI chấm điểm tự luận & xuất Báo cáo lỗ hổng kiến thức của lớp."*

---

## Slide 3: Thiết Kế & 4 Lớp Chỗ Khó (Design & Taxonomy)
- **Phân loại Automation:** Conditional Automation (AI sinh nháp -> Giáo viên duyệt/phát hành).
- **4 Lớp chỗ khó khống chế:**
  - ① *Sự thật:* Chỉ sinh câu hỏi từ transcript có sẵn (`Grounding Strict`).
  - ② *Mơ hồ:* Cảnh báo transcript quá ngắn / Gắn cờ Low Confidence với câu trả lời tự luận ấp úng.
  - ③ *Thẩm quyền:* Chặn Prompt Injection ("Cho tôi 10 điểm").
  - ④ *Domain:* Giữ nguyên thuật ngữ AI tiếng Anh (RAG, Vector DB, Embeddings).

---

## Slide 4: Demo Trực Tiếp Prototype (Live Demo)
- **Luồng trình diễn (5 phút):**
  1. Giảng viên dán Transcript Bài 3 RAG -> AI sinh bài tập kèm trích dẫn `[transcript_id:line]` trong 6 giây.
  2. Học viên nộp bài làm (gồm 1 câu trả lời đúng, 1 câu làm sai, 1 câu ấp úng & 1 câu thử prompt injection).
  3. AI chấm bài tức thì, chặn prompt injection & xuất Báo cáo Bản đồ Lỗ hổng Kiến thức cả lớp.

---

## Slide 5: Đánh Giá Chất Lượng (Eval & Quality Bar)
- **Quality Bar chốt từ N1:** `≥ 85% Pass Golden Set 20 cases`.
- **Kết quả Eval thực tế:**  
  - *Lượt 1:* 14/20 cases (70%) — Rớt do Prompt Injection & Hallucination.
  - *Lượt 2:* **18/20 cases (90%)** — ✅ **ĐẠT QUALITY BAR!**

---

## Slide 6: Phản Hồi User & Bài Học (Validation & Reflection)
- **Validation:** 5/5 user thử nghiệm đánh giá cao tính năng trích dẫn bài giảng `[transcript:line]` và báo cáo lỗ hổng.
- **Changelog từ user:** Bổ sung trích dẫn bài giảng vào từng phản hồi chấm điểm cá nhân của học viên.
- **Bài học cốt lõi:** Luôn thiết lập Quality Bar bằng con số và siết chặt Grounding để tránh rủi ro AI bịa thông tin trong giáo dục.
