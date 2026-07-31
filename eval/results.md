# Báo Cáo Tổng Hợp Golden Set Evaluation

## Thiết lập đánh giá

- **Golden Set:** 20 test cases
- **Quality bar đã chốt:** `≥ 85.0%` — tối thiểu 17/20 cases PASS
- **Lệnh chạy:** `./venv/Scripts/python.exe eval/run_eval.py`
- **Ngày đánh giá:** 2026-07-31

## Kết quả hai lượt

| Lượt | PASS | FAIL | Pass rate | So với quality bar |
|---|---:|---:|---:|---|
| Lượt 1 | 17/20 | 3/20 | 85.0% | Đạt, vừa đủ ngưỡng |
| Lượt 2 | 17/20 | 3/20 | 85.0% | Đạt, vừa đủ ngưỡng |

Chi tiết đầy đủ của từng case được lưu tại:

- [`results-luot-1.md`](results-luot-1.md)
- [`results-luot-2.md`](results-luot-2.md)

## Failure đáng chú ý

Ba case `CASE-03`, `CASE-07` và `CASE-10` đều FAIL ở cả hai lượt. Chúng cùng thuộc nhóm `normal` và mong đợi dạng `short_answer`. Đây là mẫu lỗi nhất quán cần ưu tiên xử lý ở bộ sinh câu hỏi tự luận ngắn.

## So sánh và nhận xét

- Kết quả không thay đổi giữa hai lượt.
- Không xuất hiện regression.
- Chưa có failure nào được khắc phục.
- Pass rate 85.0% chỉ vừa đủ đạt quality bar, không phải vượt xa yêu cầu.

## Hướng cải thiện

1. Rà soát prompt và logic chọn dạng câu hỏi trong `codebase/src/generator.py`.
2. Bổ sung kiểm tra đầu ra cho dạng `short_answer`.
3. Sau khi sửa, chạy lại toàn bộ 20 cases để kiểm tra cả cải thiện và regression.
4. Tiếp tục ghi nhận đầy đủ case FAIL; không thay đổi Golden Set hoặc hạ quality bar sau khi đo.

## Kết luận

Cả hai lượt đều đạt 17/20 cases, tương đương 85.0%, vừa đủ đạt quality bar. Hệ thống thể hiện kết quả ổn định qua hai lần chạy, nhưng ba failure liên quan đến `short_answer` vẫn còn và đã được đưa vào hướng cải thiện tiếp theo.
