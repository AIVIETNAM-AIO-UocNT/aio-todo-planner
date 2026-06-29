from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .label import LabelResponse


class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: TaskStatus = TaskStatus.TODO
    label_ids: List[int] = []  # list of label IDs to assign when creating the task


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[TaskStatus] = None
    label_ids: Optional[List[int]] = None  # None = leave existing labels unchanged


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    deadline: Optional[date]
    labels: List[LabelResponse] = []  # returns full label objects, not just IDs
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
