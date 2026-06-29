from config import settings
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,  
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    echo=settings.DB_ECHO,
)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("MySQL connection established successfully.")
except OperationalError as e:
    logger.critical(f"Failed to connect to MySQL: {e}")
    raise

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
