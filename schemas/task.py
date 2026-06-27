from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from enum import Enum #lớp hằng số

class TaskStatus(str, Enum): # Cố định biến Enum str
    TODO = 'todo'
    DOING = 'doing'
    DONE = 'done'

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: TaskStatus = TaskStatus.TODO # default

class TaskCreate(TaskBase):
    project_id: int

class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[TaskStatus] = None