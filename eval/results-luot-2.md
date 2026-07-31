# Báo Cáo Kết Quả Evaluation — Lượt 2

## Thông tin lượt chạy

- **Ngày chạy:** 2026-07-31
- **Vai trò:** Chạy lại toàn bộ Golden Set để kiểm tra độ ổn định
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

## So sánh với lượt 1

| Chỉ số | Lượt 1 | Lượt 2 | Thay đổi |
|---|---:|---:|---:|
| PASS | 17/20 | 17/20 | 0 |
| FAIL | 3/20 | 3/20 | 0 |
| Pass rate | 85.0% | 85.0% | 0 điểm % |
| Kết luận | Đạt | Đạt | Không đổi |

Lượt 2 không xuất hiện regression: không có case PASS nào chuyển thành FAIL. Tuy nhiên, cũng chưa có case FAIL nào chuyển thành PASS.

## Phân tích các failure còn lại

Các case CASE-03, CASE-07 và CASE-10 tiếp tục FAIL ở lượt 2. Cả ba đều mong đợi dạng short_answer, cho thấy đây là mẫu lỗi lặp lại thay vì lỗi ngẫu nhiên của một case riêng lẻ.

### Hướng cải thiện tiếp theo

- Điều chỉnh prompt hoặc quy tắc chọn loại câu hỏi trong codebase/src/generator.py.
- Kiểm tra riêng điều kiện sinh short_answer, nhưng sau khi sửa vẫn phải chạy lại toàn bộ Golden Set.
- Giữ nguyên quality bar và expected output; không sửa bộ test chỉ để tăng pass rate.

## Kết luận lượt 2

Hệ thống duy trì kết quả 17/20, tương đương 85.0%, vừa đủ đạt quality bar. Kết quả cho thấy độ ổn định giữa hai lượt, đồng thời xác định short_answer là khu vực cần ưu tiên cải thiện.
