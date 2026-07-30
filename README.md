# 🎓 VLearn EduAI — Hệ Thống Sinh Bài Tập Tự Động & Phân Tích Hiệu Quả Học Tập

**Dự án Mini Hackathon AI — Batch 03 (Lớp K4 - Group 04 - Zone 2)**  
> **Chủ đề (Track A - VLearn):** Sinh bài tập tự động từ bài giảng & Phân tích lỗ hổng kiến thức theo từng buổi học.

---

## 👥 Thành Viên Nhóm & Phân Công Chi Tiết

| Mã HV | Họ và Tên | Vai trò | Phân công công việc (Tên phần đảm nhận) |
|---|---|---|---|
| **2A202601284** | **Nguyễn Văn Hưng** | Trưởng Nhóm | AI Spec (`spec.md`), Prompt & Engine LangGraph Generator (`codebase/src/generator.py`), Đóng góp Golden Set (`eval/`). |
| **2A202601108** | **Đặng Minh Quang** | Thành viên | Xây dựng bộ kiểm thử Golden Set (`eval/golden_set.json`), Chạy Eval 2 lượt & Báo cáo kết quả (`eval/results.md`), User Validation Log (`validation/user_test_log.md`). |
| **2A202601372** | **Nhữ Văn Hùng** | Thành viên | Phát triển Auto Grader (`codebase/src/grader.py`), Engine Báo cáo Lỗ hổng (`codebase/src/analytics.py`), API Server (`codebase/src/api.py`), Slide Demo (`demo-slides.md`). |

---

## 🎯 Lát Cắt Dự Án (One-Sentence Slice)

> *"Giảng viên đưa transcript bài giảng -> AI phân tích nội dung để tự động sinh 5 câu bài tập (trắc nghiệm, điền khuyết, tự luận) kèm đáp án & trích dẫn -> Học viên nộp bài -> AI chấm điểm tự luận & xuất Báo cáo lỗ hổng kiến thức của lớp."*

---

## 📁 Cấu Trúc Repository Chuẩn Hackathon

```text
K4-hackathon-HHQ-E402/
├── README.md               ← Danh sách thành viên + Phân công công việc + Tổng quan repo
├── spec.md                 ← AI Spec 8 phần + §9 Changelog (nộp trước 23:59 N1)
├── demo-slides.md          ← Slide trình bày Demo 6 trang (Outline chuẩn §5.1)
├── codebase/               ← Prototype chạy thật (Working Engine)
│   ├── README.md           ← Hướng dẫn chạy codebase & bảng ma trận tính năng
│   ├── requirements.txt
│   └── src/
│       ├── main.py         ← CLI Demo & Server Launcher
│       ├── config.py       ← Cấu hình biến môi trường
│       ├── generator.py    ← Engine sinh bài tập kèm trích dẫn [transcript:line]
│       ├── grader.py       ← Engine tự động chấm trắc nghiệm & tự luận ngắn
│       ├── analytics.py    ← Engine phân tích & xuất báo cáo lỗ hổng kiến thức
│       └── api.py          ← RESTful API Server (FastAPI)
├── eval/                   ← Đánh giá chất lượng (Evaluation)
│   ├── golden_set.json     ← Bộ kiểm thử 20 cases (10 thường + 8 chỗ khó + 2 hiếm)
│   └── results.md          ← Bảng kết quả các lượt chạy eval (Đạt 90% Pass Rate)
├── validation/             ← Nhật ký thử nghiệm với người dùng
│   └── user_test_log.md    ← Log feedback nguyên văn từ 5 người dùng ngoài nhóm
└── reflection/             ← Reflection cá nhân (mỗi người 1 file)
    ├── hung_nguyen_2A202601284.md
    ├── quang_dang_2A202601108.md
    └── hung_nhu_2A202601372.md
```

---

## ⚡ Quick Start — Trải Nghiệm Prototype

```bash
# 1. Chạy CLI Demo (Xem luồng Sinh bài tập -> Chấm điểm -> Báo cáo lỗ hổng)
python codebase/src/main.py

# 2. Hoặc khởi chạy Web API Server (FastAPI)
python codebase/src/main.py --server
```
👉 Truy cập Swagger UI tại: **http://localhost:8000/docs**

---

## 📊 Kết Quả Đánh Giá (Quality Bar)

- **Quality Bar đặt ra:** `≥ 85% Pass Golden Set 20 cases`
- **Kết quả Eval Lượt 2:** **18/20 Cases Pass (90.0%)** — ✅ **ĐẠT QUALITY BAR!**
