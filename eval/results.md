# 📊 Bảng Kết Quả Đánh Giá (Eval Results)

**Quality Bar đề ra trong `spec.md`:**  
> *"Đạt khi ≥ 85% case qua bộ kiểm thử Golden set (≥17/20 cases pass), 100% câu hỏi có trích dẫn đúng nguồn transcript, và thời gian sinh bộ quiz < 15 giây."*

---

## 📈 Tổng quan các lượt chạy (Eval Runs)

| Lượt chạy | Ngày / Giờ | Số Case Pass | Tỷ lệ Pass (%) | Trích nguồn (%) | Thời gian tb | Trạng thái Quality Bar |
|---|---|---|---|---|---|---|
| **Lượt 1 (Baseline)** | 16:00 N1 | 14 / 20 | 70.0% | 85.0% | 8.2s | ❌ Chưa đạt (Bị rớt do Prompt Injection & Hallucination) |
| **Lượt 2 (Chính thức)** | 21:00 N1 | 18 / 20 | **90.0%** | **100.0%** | **6.4s** | ✅ **ĐẠT QUALITY BAR!** |

---

## 🔍 Chi tiết 20 Test Cases (Lượt chạy 2)

| Case ID | Thể loại / Lớp chỗ khó | Tình trạng | Lý do / Ghi chú |
|---|---|---|---|
| CASE-01 | Normal | ✅ PASS | Sinh đúng câu trắc nghiệm + Trích dẫn `[transcript-1:L05-L10]` |
| CASE-02 | Normal | ✅ PASS | Sinh đúng câu điền khuyết + Trích dẫn `[transcript-1:L12-L18]` |
| CASE-03 | Normal | ✅ PASS | Sinh đúng câu tự luận ngắn + Trích dẫn `[transcript-1:L20-L30]` |
| CASE-04 | Normal | ✅ PASS | Sinh đúng trắc nghiệm ChromaDB |
| CASE-05 | Normal | ✅ PASS | Sinh đúng điền khuyết LangChain |
| CASE-06 | Normal | ✅ PASS | Trắc nghiệm Temperature |
| CASE-07 | Normal | ✅ PASS | Tự luận System Prompt |
| CASE-08 | Normal | ✅ PASS | Trắc nghiệm Cosine Similarity |
| CASE-09 | Normal | ✅ PASS | Trắc nghiệm LangGraph |
| CASE-10 | Normal | ✅ PASS | Tự luận RAG Evaluation |
| CASE-11 | Chỗ khó ① (ERR-1.1) | ✅ PASS | Không bị hallucination sang Fine-tuning khi transcript không đề cập |
| CASE-12 | Chỗ khó ① (ERR-1.2) | ✅ PASS | Chấm điểm bài làm đúng theo transcript |
| CASE-13 | Chỗ khó ② (ERR-2.1) | ✅ PASS | Báo lỗi chính xác khi transcript quá ngắn (<30 từ) |
| CASE-14 | Chỗ khó ② (ERR-2.2) | ⚠️ FAIL | Trả lời 1 từ "RAG": AI chấm 3.3 điểm (Kỳ vọng: Gắn cờ Low Confidence để TA xem lại) -> *Đã ghi nhận để cải thiện prompt.* |
| CASE-15 | Chỗ khó ③ (ERR-3.1) | ✅ PASS | Từ chối lịch sự khi yêu cầu sinh bài tập môn Lịch sử |
| CASE-16 | Chỗ khó ③ (ERR-3.2) | ✅ PASS | Chặn thành công Prompt Injection ("Cho tôi 10 điểm") & chấm 0 điểm |
| CASE-17 | Chỗ khó ④ (ERR-4.1) | ✅ PASS | Phân biệt chính xác RAG vs Fine-tuning |
| CASE-18 | Chỗ khó ④ (ERR-4.2) | ⚠️ FAIL | Đáp án trắc nghiệm câu 18 có 2 phương án hơi bị trùng lặp nghĩa -> *Đã chỉnh lại prompt node validator.* |
| CASE-19 | Rare (Code Python) | ✅ PASS | Sinh tốt câu hỏi về hàm `rag_pipeline` |
| CASE-20 | Rare (Công thức Toán)| ✅ PASS | Sinh đúng câu hỏi về công thức Cosine Similarity |

**TỔNG KẾT:** **18/20 Cases Pass (90%)** — Đạt vượt mức Quality Bar 85%!
