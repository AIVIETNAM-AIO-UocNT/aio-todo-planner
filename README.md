📅 AIO Todo Planner

Dự án lập kế hoạch công việc (Todo Planner) sử dụng FastAPI cho Backend, Streamlit cho Frontend và quản lý môi trường/package thông qua công cụ hiện đại uv.

🚀 Hướng dẫn khởi chạy dự án (How to Run)

Để khởi chạy dự án dưới máy local (môi trường phát triển cá nhân), bạn vui lòng thực hiện tuần tự theo các bước chi tiết bên dưới.

📋 Yêu cầu tiên quyết (Prerequisites)

Đảm bảo máy tính của bạn đã cài đặt công cụ quản lý package uv. Nếu chưa cài đặt, bạn có thể cài nhanh bằng lệnh sau:

# Cài đặt uv qua pip
pip install uv


💻 Các bước thực hiện chi tiết

Bạn cần mở 2 Terminal (Cửa sổ dòng lệnh) riêng biệt và cả 2 cửa sổ đều di chuyển vào thư mục gốc của dự án aio-todo-planner:

cd đường_dẫn_đến/aio-todo-planner


🖥️ Terminal 1: Khởi chạy Backend (FastAPI)

Thực hiện lần lượt các câu lệnh sau để cài đặt môi trường, tạo cơ sở dữ liệu và khởi chạy server API:

Khởi tạo môi trường ảo và cài đặt các thư viện cần thiết cho Backend:

uv sync --directory backend


Khởi tạo cơ sở dữ liệu ban đầu (Database Initialization):

uv run --directory backend python init_db.py


Bắt đầu chạy Server Backend:

uv run --directory backend uvicorn main:app --reload --host localhost --port 8000


Sau khi chạy thành công, tài liệu API (Swagger UI) sẽ có tại địa chỉ: 👉 http://localhost:8000/docs

🖥️ Terminal 2: Khởi chạy Frontend (Streamlit)

Thực hiện các câu lệnh sau ở cửa sổ dòng lệnh thứ hai để cài đặt môi trường và khởi chạy giao diện người dùng:

Khởi tạo môi trường ảo và cài đặt các thư viện cần thiết cho Frontend:

uv sync --directory frontend


Chạy ứng dụng Frontend với Streamlit:

uv run --project frontend streamlit run frontend/app.py --server.port 8501


Sau khi chạy thành công, giao diện ứng dụng sẽ tự động mở ra trên trình duyệt của bạn hoặc truy cập tại địa chỉ: 👉 http://localhost:8501
