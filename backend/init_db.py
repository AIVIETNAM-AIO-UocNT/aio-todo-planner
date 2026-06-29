"""
init_db.py — Tạo tất cả bảng trong MySQL.

Chỉ chạy một lần khi setup môi trường mới:
    python init_db.py

Với bảng đã tồn tại: bỏ qua, không xóa data.
Với thay đổi schema (thêm cột...): dùng Alembic thay thế.
"""

import logging
import sys

import models  # noqa: F401 — kích hoạt đăng ký tất cả models vào Base.metadata
from database import Base, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def init_db() -> None:
    table_names = list(Base.metadata.tables.keys())
    logger.info(f"Sẽ tạo các bảng: {', '.join(table_names)}")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Khởi tạo database thành công.")
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_db()
