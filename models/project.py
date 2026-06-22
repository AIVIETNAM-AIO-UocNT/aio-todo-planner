
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(255), nullable=False)
    description = Column(Text)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)