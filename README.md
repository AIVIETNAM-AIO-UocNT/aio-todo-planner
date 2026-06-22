# TO_DO_LIST

Project quản lý công việc sử dụng Python + SQLAlchemy + MySQL.

## 1. Clone project

```bash
git clone <repository_url>
cd TO_DO_LIST
```

## 2. Tạo môi trường ảo (khuyến nghị)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

MacOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

## 4. Tạo file `.env`

Thêm biến môi trường:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/todo_list
```

Ví dụ:

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost/todo_list
```


## 5. Khởi tạo các bảng

Chạy:

```bash
python init_db.py
```

Nếu thành công sẽ hiển thị:

```
Database initialized successfully!

chạy thành công
```

## Cấu trúc database

- users
- projects
- tasks
- labels
- task_labels

## Cấu trúc thư mục

```
TO_DO_LIST/
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── label.py
│   └── task_label.py
│
├── database.py
├── init_db.py
├── requirements.txt
├── .env
└── README.md
```