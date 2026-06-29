"""
init_db.py — Create all tables in MySQL.

Run once when setting up a new environment:
    python init_db.py

Existing tables are skipped; no data is deleted.
For schema changes (adding columns, etc.): use Alembic instead.
"""

import logging
import sys

import models 
from database import Base, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def init_db() -> None:
    table_names = list(Base.metadata.tables.keys())
    logger.info(f"Tables to create: {', '.join(table_names)}")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_db()
