from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Date, ForeignKey, Enum
from sqlalchemy.sql import func

from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(255), nullable=False)
    description = Column(Text)

    status = Column(
        Enum("todo", "doing", "done"),
        default="todo"
    )

    deadline = Column(Date)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)

    labels = relationship(
        "Label", 
        secondary="task_labels", 
        back_populates="tasks", 
        cascade="all, delete"
    )