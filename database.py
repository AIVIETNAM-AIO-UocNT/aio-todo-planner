import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker  # Giữ lại sessionmaker từ main
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy chuỗi DATABASE_URL từ file .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Kiểm tra xem cấu hình đã tồn tại chưa, nếu chưa thì báo lỗi bắt buộc
if not DATABASE_URL:
    raise ValueError(
        "LỖI: Chưa tìm thấy cấu hình DATABASE_URL! "
        "Vui lòng tạo file .env dựa trên file .env.example cấu hình."
    )

engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()