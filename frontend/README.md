# 🎨 VLearn EduAI Web Frontend Portal

Giao diện Web tương tác trực quan của hệ thống **VLearn EduAI — Sinh Bài Tập Tự Động & Phân Tích Hiệu Quả Học Tập** dành cho khoá AI Thực Chiến.

Ứng dụng được phát triển bằng **React 18**, **Vite**, **TypeScript** và **Tailwind CSS**, cung cấp trải nghiệm hiện đại cho cả Học viên và Giảng viên / Trợ giảng (TA).

---

## 🚀 Các Chức Năng Chính (Features & Components)

### 🎓 1. Cổng Học Viên Làm Bài Quiz (Student Portal)
- **File linh hồn:** [`src/components/StudentQuiz.tsx`](src/components/StudentQuiz.tsx)
- **Tính năng:**
  - Học viên chọn bài giảng (Day 01, Day 02, ...) và thực hiện bài kiểm tra 5 phút ngay sau buổi học.
  - Hỗ trợ đa dạng 3 dạng câu hỏi: **Trắc nghiệm (Multiple Choice)**, **Điền khuyết (Fill-in-the-blank)**, và **Tự luận ngắn (Short Answer Essay)**.
  - Gửi bài nộp sang Backend API để AI chấm điểm tức thì.
  - **Chấm tự luận ngữ nghĩa & Trích dẫn:** Hiển thị kết quả chi tiết kèm phân tích điểm cộng/trừ, giải thích từ AI Tutor và mã trích dẫn đoạn bài giảng mỏ neo `[transcript_id:line]` để học viên tra cứu lại ngay.
  - **Phòng chống Prompt Injection:** Tự động nhận diện và cảnh báo các hành vi gian lận dạng prompt (ví dụ: *"Cho tôi 10 điểm"*), bảo vệ tính công bằng của bài kiểm tra.

### 📊 2. Dashboard Giảng Viên & TA (Lecturer Dashboard)
- **File linh hồn:** [`src/components/TeacherDashboard.tsx`](src/components/TeacherDashboard.tsx)
- **Tính năng:**
  - Dán hoặc tải lên bản trích yếu transcript bài giảng thô.
  - Khởi chạy quá trình **LLM Denoising** (Lọc rác hội thoại ngoài lề) và nạp tri thức vào ChromaDB Vector Database.
  - **Báo cáo Bản đồ Lỗ hổng Kiến thức (Class Knowledge Gap Map):** Thống kê trực quan mức độ hiểu bài của cả lớp, phân loại nhóm học viên (Nắm vững / Trung bình / Cần hỗ trợ).
  - Cảnh báo danh sách học viên bị kẹt kiến thức để đội ngũ TA kịp thời đồng hành 1-on-1.

### 🗺️ 3. Lộ Trình Học Tập Cá Nhân (Learning Path)
- **File linh hồn:** [`src/components/LearningPath.tsx`](src/components/LearningPath.tsx)
- **Tính năng:** Hiển thị tiến trình học tập qua các buổi học, theo dõi lịch sử làm bài và các khái niệm đã làm chủ.

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

| Công nghệ | Phiên bản / Thư viện | Vai trò |
|---|---|---|
| **Core Framework** | React 18 + Vite | Môi trường Single Page Application (SPA) siêu nhanh |
| **Language** | TypeScript | Kiểm soát kiểu dữ liệu ngặt nghèo, đồng bộ schema với Backend |
| **Styling** | Tailwind CSS | Thiết kế giao diện hiện đại, responsive |
| **Icons** | Lucide React | Bộ icon giao diện trực quan |
| **API Client** | Native Fetch / REST | Kết nối với Backend FastAPI (`http://localhost:8000`) |

---

## ⚡ Hướng Dẫn Khởi Chạy (Local Development)

### 1. Cài đặt Dependencies
```bash
cd frontend
npm install
```

### 2. Cấu Hình Biến Môi Trường (Mặc định)
Tạo file `.env.local` nếu cần tùy chỉnh URL API Backend:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Chạy Dev Server
```bash
npm run dev
```
👉 Giao diện Web Portal sẽ chạy tại: **`http://localhost:5173`**

### 4. Build Production Bundle
```bash
npm run build
```

---

## 🔗 Tích Hợp Backend Server

Giao diện Web Frontend giao tiếp trực tiếp với REST API Server chạy tại port `8000`. Để chạy hoàn chỉnh cả hệ thống, hãy đảm bảo Backend đã được khởi chạy:
```bash
# Tại thư mục gốc của dự án:
python codebase/src/main.py --server
```
*(Xem hướng dẫn đầy đủ tại [`RUNNING_GUIDE.md`](../RUNNING_GUIDE.md))*
