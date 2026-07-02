# Hướng dẫn chạy dự án To-Do Planner

## 1. Chạy Backend

Mở *Terminal 1* và di chuyển đến thư mục gốc của dự án:

cd to-do-planner

### Bước 1. Cài đặt dependencies

uv sync --directory backend

### Bước 2. Khởi tạo cơ sở dữ liệu

uv run --directory backend python init_db.py

### Bước 3. Khởi động Backend

uv run --directory backend uvicorn main:app --reload --host localhost --port 8000

Sau khi backend khởi động thành công, mở trình duyệt và truy cập:

http://localhost:8000/docs

---

## 2. Tạo người dùng đầu tiên

Trong trang Swagger (/docs):

1. Tìm API **/users**.
2. Nhấn *Try it out*.
3. Nhập đầy đủ các thông tin theo yêu cầu.
4. Nhấn *Execute*.
5. Kiểm tra kết quả trả về.

**Lưu ý:** Cần tạo người dùng thành công trước khi sử dụng giao diện Frontend.


---

## 3. Chạy Frontend

Mở *Terminal 2* (độc lập với Terminal chạy Backend) và đứng tại thư mục gốc của dự án:

cd to-do-planner

### Bước 1. Cài đặt dependencies

uv sync --directory frontend

### Bước 2. Khởi động Streamlit

uv run --project frontend streamlit run frontend/app.py --server.port 8501

Sau khi chạy thành công, Streamlit sẽ mở trên trình duyệt (thường tại địa chỉ http://localhost:8501).

---

## 4. Thiết lập giao diện

Sau khi mở giao diện Streamlit:

1. Chuyển giao diện sang chế độ *Light*.

### Lưu ý cho lập trình viên

Hiện tại cần chỉnh sửa trong source code để *Light* trở thành giao diện mặc định khi khởi động ứng dụng, thay vì yêu cầu người dùng tự chuyển mỗi lần sử dụng.

---

# Tóm tắt quy trình

1. Chạy Backend.
2. Khởi tạo database.
3. Mở Swagger tại http://localhost:8000/docs.
4. Tạo ít nhất một người dùng thông qua API /users.
5. Chạy Frontend.
6. Mở Streamlit.
7. Đảm bảo giao diện mặc định là *Light*.