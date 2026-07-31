# Nhật Ký Thử Nghiệm Với Người Dùng (User Validation Log)

## Thông tin đợt thử nghiệm

- **Ngày thực hiện validation:** 2026-07-31
- **Phiên bản/commit tham chiếu:** `1970e43`
- **Số người thử mục tiêu:** 5 người ngoài nhóm
- **Willing users từ CP1:** User_A (TA khóa AI), User_B (Học viên khóa AI)
- **Task chung:** Dùng VLearn EduAI để tạo bài tập từ transcript, làm bài, xem kết quả chấm và kiểm tra báo cáo lỗ hổng kiến thức.

## Kịch bản mỗi phiên

1. Giao task cho người thử và không hướng dẫn trong lúc họ thao tác.
2. Ghi lại thứ tự thao tác, điểm bị kẹt và việc họ có hoàn thành task hay không.
3. Hỏi ba câu:
   - “Điều gì khó hiểu hoặc khó chịu nhất?”
   - “Bạn có tin kết quả này không? Vì sao?”
   - “Bạn có dùng sản phẩm này thật không? Vì sao hoặc vì sao chưa?”
4. Chép nguyên văn câu trả lời vào bảng.

## Feedback Log

| STT | Người thử  | Vai trò / Willing user?               | Task                                            | Quan sát                                                                             | Quote nguyên văn                                                                   | Mức nghiêm trọng | Quyết định/Hành động                                            |
| --: | ---------- | ------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- | ---------------- | --------------------------------------------------------------- |
|   1 | **User_A** | Học viên khóa AI / Willing user (CP1) | Tải transcript và tạo bộ câu hỏi                | Hoàn thành task nhưng dừng lại vài giây để tìm nút tạo bài tập.                      | “Tôi tạo được câu hỏi, nhưng nút tạo bài tập nên nổi bật hơn.”                     | Medium           | Tăng độ tương phản và đổi nhãn nút thành “Tạo bài tập”.         |
|   2 | **User_B** | Học viên khóa AI / Willing user (CP1) | Làm quiz và xem điểm                            | Hoàn thành quiz; hiểu điểm tổng nhưng chưa chú ý phần trích dẫn.                     | “Tôi muốn bấm vào trích dẫn để quay lại đúng đoạn bài học.”                        | Medium           | Cho phép bấm citation để mở đoạn transcript nguồn.              |
|   3 | **User_C** | Học viên khóa AI / Không              | Trả lời câu tự luận và đọc feedback             | Đọc feedback kỹ nhưng không hiểu rõ vì sao bị trừ một phần điểm.                     | “Phần giải thích hữu ích, nhưng cần nói rõ tôi thiếu ý nào.”                       | High             | Bổ sung các ý còn thiếu và đoạn bài học cần ôn trong feedback.  |
|   4 | **User_D** | Học viên khóa AI / Không              | Xem báo cáo lỗ hổng kiến thức                   | Xác định được chủ đề yếu nhưng hỏi báo cáo thuộc lớp và buổi học nào.                | “Nếu có tên lớp và buổi học thì tôi sẽ dễ dùng báo cáo hơn.”                       | Medium           | Bổ sung tên lớp, buổi học và transcript nguồn vào báo cáo.      |
|   5 | **User_E** | Học viên khóa AI / Không              | Thử nhập câu trả lời mang tính prompt injection | Hệ thống từ chối yêu cầu gian lận và trả về cảnh báo; người thử vẫn hoàn thành task. | “Hệ thống không cho điểm theo yêu cầu, nhưng cảnh báo có thể viết thân thiện hơn.” | Low              | Giữ cơ chế chặn và viết lại cảnh báo theo hướng thân thiện hơn. |

## Tổng hợp kết quả

- **Chủ đề lặp lại nhiều nhất:** Người dùng cần liên kết rõ hơn giữa kết quả, feedback và transcript nguồn.
- **Failure nghiêm trọng nhất:** Feedback tự luận chưa chỉ rõ ý còn thiếu, có thể làm giảm độ tin cậy vào điểm AI.
- **1–2 thay đổi đề xuất trước demo:** Làm citation dễ nhận biết; bổ sung ý còn thiếu trong feedback tự luận.
- **Nội dung đề xuất giữ nguyên:** Cơ chế chặn prompt injection vì hoạt động đúng mục tiêu an toàn.
- **Nội dung đề xuất đưa vào backlog:** Citation có thể nhấp và metadata tên lớp/buổi học trong báo cáo.

## Changelog đề xuất từ kết quả thử nghiệm

### Đề xuất 1

- **Feedback nguồn:** User_C
- **Vấn đề:** Feedback tự luận chưa chỉ rõ ý còn thiếu.
- **Đề xuất thay đổi:** Hiển thị ý đúng, ý thiếu và citation cần ôn.
- **File dự kiến liên quan:** `codebase/src/grader.py`, `frontend/src/components/StudentQuiz.tsx`
- **Trạng thái:** Đang xử lý

### Đề xuất 2

- **Feedback nguồn:** User_E
- **Vấn đề:** Cảnh báo prompt injection chưa thân thiện.
- **Đề xuất:** Giữ cơ chế chặn, chỉ điều chỉnh câu chữ cảnh báo.
- **File dự kiến liên quan:** `codebase/src/grader.py`
- **Trạng thái:** Đang xử lý
