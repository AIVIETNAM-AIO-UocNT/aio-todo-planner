from database import Base
from sqlalchemy import Column, ForeignKey, Integer


class TaskLabel(Base):
    __tablename__ = "task_labels"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    label_id = Column(Integer, ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True)
