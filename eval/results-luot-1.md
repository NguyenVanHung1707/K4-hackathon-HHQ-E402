# Báo Cáo Kết Quả Evaluation — Lượt 1

## Thông tin lượt chạy

- **Ngày chạy:** 2026-07-31
- **Vai trò:** Baseline trước khi đánh giá lại
- **Bộ kiểm thử:** Golden Set gồm 20 cases
- **Số case PASS:** **17/20**
- **Số case FAIL:** **3/20**
- **Pass rate:** **85.0%**
- **Quality bar:** ≥ 85.0%
- **Kết luận:** ✅ **ĐẠT QUALITY BAR, vừa đủ ngưỡng yêu cầu**

## Chi tiết 20 test cases

| Case ID | Category | Dạng bài tập mong muốn | Trạng thái |
|---|---|---|---|
| **CASE-01** | `normal` | `multiple_choice` | PASS ✅ |
| **CASE-02** | `normal` | `fill_in_blank` | PASS ✅ |
| **CASE-03** | `normal` | `short_answer` | FAIL ❌ |
| **CASE-04** | `normal` | `multiple_choice` | PASS ✅ |
| **CASE-05** | `normal` | `fill_in_blank` | PASS ✅ |
| **CASE-06** | `normal` | `multiple_choice` | PASS ✅ |
| **CASE-07** | `normal` | `short_answer` | FAIL ❌ |
| **CASE-08** | `normal` | `multiple_choice` | PASS ✅ |
| **CASE-09** | `normal` | `multiple_choice` | PASS ✅ |
| **CASE-10** | `normal` | `short_answer` | FAIL ❌ |
| **CASE-11** | `edge_class_1` | `multiple_choice` | PASS ✅ |
| **CASE-12** | `edge_class_1` | `multiple_choice` | PASS ✅ |
| **CASE-13** | `edge_class_2` | `multiple_choice` | PASS ✅ |
| **CASE-14** | `edge_class_2` | `multiple_choice` | PASS ✅ |
| **CASE-15** | `edge_class_3` | `multiple_choice` | PASS ✅ |
| **CASE-16** | `edge_class_3` | `multiple_choice` | PASS ✅ |
| **CASE-17** | `edge_class_4` | `multiple_choice` | PASS ✅ |
| **CASE-18** | `edge_class_4` | `multiple_choice` | PASS ✅ |
| **CASE-19** | `rare` | `short_answer` | PASS ✅ |
| **CASE-20** | `rare` | `multiple_choice` | PASS ✅ |

## Phân tích kết quả lượt 1

Lượt chạy baseline đạt 17/20 cases. Ba case chưa đạt là CASE-03, CASE-07 và CASE-10. Cả ba đều thuộc nhóm
ormal và cùng mong đợi dạng câu hỏi short_answer.

### Mẫu lỗi quan sát được

- Các dạng multiple_choice và ill_in_blank trong bộ test đều đạt.
- CASE-19 cho thấy hệ thống vẫn có thể sinh short_answer thành công ở một trường hợp hiếm.
- Tuy nhiên, ba case short_answer thông thường chưa đạt tiêu chí của bộ Eval. Điều này cho thấy khả năng lựa chọn dạng câu hỏi hoặc bao phủ nội dung kỳ vọng cho short_answer chưa ổn định.

### Hướng xử lý đề xuất

- Rà soát prompt và quy tắc chọn loại câu hỏi trong codebase/src/generator.py.
- Bổ sung bước kiểm tra đầu ra có đúng loại short_answer theo yêu cầu hay không.
- Chạy lại toàn bộ 20 cases sau mỗi thay đổi để phát hiện regression.

## Kết luận lượt 1

Lượt 1 đạt đúng 85.0%, vừa đủ đạt quality bar. Ba failure vẫn được giữ nguyên trong báo cáo để làm baseline và phục vụ phân tích ở lượt tiếp theo.
