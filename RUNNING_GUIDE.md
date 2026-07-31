# 🚀 Hướng Dẫn Vận Hành & Khởi Chạy Hệ Thống VLearn EduAI (Chạy Local)

Tài liệu này hướng dẫn chi tiết các bước cài đặt và khởi chạy hệ thống **VLearn EduAI** trực tiếp trên máy tính của bạn (không dùng Docker).

---

## 📋 1. Yêu Cầu Tiền Đề (Prerequisites)

- **Python**: Phiên bản 3.10 trở lên.
- **Node.js**: Phiên bản 18 hoặc 20 trở lên.
- **Git**: Đã cài đặt trên máy.

---

## 🔑 2. Cấu Hình Biến Môi Trường (Environment Variables)

Tạo file `.env` ở thư mục gốc của dự án (nếu chưa có) và điền API Key của Google Gemini:

```env
GEMINI_API_KEY=AIzaSy... (API Key Gemini của bạn)
OPENAI_API_KEY=sk-... (Tùy chọn nếu dùng OpenAI fallback)
LLM_MODEL_NAME=gpt-4o-mini
DATA_DIR=data
```

---

## ⚡ 3. Các Bước Khởi Chạy Chi Tiết

### 🔹 Bước 1: Kích Hoạt Môi Trường Ảo Python & Cài Thư viện Backend

Mở cửa sổ Terminal thứ nhất ở thư mục gốc dự án:

```powershell
# Kích hoạt venv (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Cài đặt thư viện Python (nếu chưa cài)
pip install -r codebase/requirements.txt
```

### 🔹 Bước 2: Khởi Chạy Backend REST API Server (FastAPI)

Tại cửa sổ Terminal thứ nhất (sau khi đã kích hoạt `.venv`):

```powershell
python codebase/src/main.py --server
```

> 🟢 **Trạng thái thành công:** Terminal báo `Uvicorn running on http://0.0.0.0:8000`.

---

### 🔹 Bước 3: Cài Đặt & Khởi Chạy Frontend (React Vite)

Mở cửa sổ Terminal thứ hai tại thư mục gốc dự án:

```powershell
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt thư viện Node (chỉ chạy 1 lần đầu)
npm install

# Khởi chạy giao diện Web
npm run dev
```

> 🟢 **Trạng thái thành công:** Terminal báo `Local: http://localhost:5173/`.

---

## 🌐 4. Mở Giao Diện Web & Trải Nghiệm

Sau khi khởi chạy cả 2 server, bạn truy cập vào trình duyệt:
- 🎓 **Web Portal:** `http://localhost:5173`
- 📚 **Swagger API Docs (Backend):** `http://localhost:8000/docs`

---

## 🎬 5. Kịch Bản Demo Cho Ban Giám Khảo (Flow Demo)

### 🎓 Luồng Sinh Viên Làm Bài Quiz (Student Portal):
1. Truy cập `http://localhost:5173` $\rightarrow$ Nhập MSSV và Họ tên sinh viên.
2. Chọn bài học tại Sidebar (ví dụ: *Day 01*).
3. Bấm nút **"Yêu cầu AI sinh bộ đề bài"** $\rightarrow$ Hệ thống sẽ dùng **Gemini 2.0 Flash** cá nhân hóa bộ câu hỏi chỉ trong **1-2 giây**.
4. Thực hiện làm bài (Trắc nghiệm, Điền từ, Tự luận) và bấm **Nộp bài**.
5. AI Auto-Grader chấm điểm theo ngữ nghĩa và hiển thị phản hồi ngay lập tức.

### 🖥️ Luồng Giảng Viên Quản Lý (Teacher Dashboard):
1. Chuyển sang tab **"Giảng Viên"** trên menu top bar.
2. Nạp thêm file transcript/học liệu mới để mở rộng kiến thức bài giảng.
3. Xem **Bản Đồ Lỗ Hổng Kiến Thức (Knowledge Gap Map)** tổng hợp tình hình học tập của cả lớp.
