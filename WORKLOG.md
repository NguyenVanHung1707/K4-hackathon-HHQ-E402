# Worklog — Nhóm 04 (VLearn EduAI)

> Nhật ký ghi nhận tiến độ công việc hàng ngày của nhóm 04 theo chuẩn dự án P-140.

---

## 📅 Day 1: 2026-07-29

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| **Nguyễn Văn Hưng** | Khảo sát nhu cầu bài toán & Viết AI Spec (§1-§4) | ✅ Done | [spec.md](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/spec.md) | 4h |
| **Nguyễn Văn Hưng** | Khởi tạo cấu trúc dự án & LangGraph Quiz Generator Engine | ✅ Done | [codebase/src/generator.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/generator.py) | 3h |
| **Đặng Minh Quang** | Thu thập dữ liệu chatlog & Thiết kế Golden Set 20 cases | ✅ Done | [eval/golden_set.json](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/eval/golden_set.json) | 3.5h |
| **Đặng Minh Quang** | Chạy thử nghiệm Eval lượt 1 (Baseline 70% Pass) | ✅ Done | [eval/results.md](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/eval/results.md) | 2h |
| **Nhữ Văn Hùng** | Xây dựng SQLite DB & ChromaDB Vector Store Module | ✅ Done | [codebase/src/db.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/db.py), [vector_store.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/vector_store.py) | 4h |
| **Nhữ Văn Hùng** | Phát triển Auto-Grader & Phòng chống Prompt Injection | ✅ Done | [codebase/src/grader.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/grader.py) | 3h |

**Tổng kết ngày 1:** Hoàn thành AI Spec, dựng xong móng backend (LLM Generator, Auto Grader, SQLite DB, Vector Store) và bộ Golden Set 20 cases.

---

## 📅 Day 2: 2026-07-30

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| **Nguyễn Văn Hưng** | Phát triển LLM Denoising & Anchor-Enrichment RAG Retrieval | ✅ Done | [codebase/src/denoiser.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/denoiser.py) | 3.5h |
| **Nguyễn Văn Hưng** | Hoàn thiện tài liệu Mô tả Workflow & Sơ đồ Mermaid | ✅ Done | [WORKFLOW.md](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/WORKFLOW.md) | 2.5h |
| **Đặng Minh Quang** | Chạy thử nghiệm Eval lượt 2 (Đạt 90% Pass Quality Bar) | ✅ Done | [eval/results.md](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/eval/results.md) | 2.5h |
| **Đặng Minh Quang** | Phỏng vấn thử nghiệm với 5 người dùng & tổng hợp User Log | ✅ Done | [validation/user_test_log.md](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/validation/user_test_log.md) | 3h |
| **Nhữ Văn Hùng** | Phát triển Persona Extractor & Class Knowledge Gap Analytics | ✅ Done | [codebase/src/persona.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/persona.py), [analytics.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/analytics.py) | 3.5h |
| **Nhữ Văn Hùng** | Phát triển Frontend Next.js / React UI & RESTful FastAPI Server | ✅ Done | [frontend/](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/frontend/), [codebase/src/api.py](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/codebase/src/api.py) | 4h |
| **Cả nhóm** | Biên soạn Dàn ý Slide Demo 6 trang & Viết Reflection | ✅ Done | [demo-slides.md](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/demo-slides.md), [reflection/](file:///e:/hung/VinAI/Lab/Lab5/K4-hackathon-HHQ-E402/reflection/) | 2h |

**Tổng kết ngày 2:** Đã hoàn thiện toàn bộ mã nguồn Backend/Frontend, chạy Eval đạt 90% Pass Rate, hoàn thành thử nghiệm với 5 user và sẵn sàng cho vòng Demo!
