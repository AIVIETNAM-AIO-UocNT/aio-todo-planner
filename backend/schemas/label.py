from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LabelCreate(BaseModel):
    name: str
    color: Optional[str] = None


class LabelUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class LabelResponse(BaseModel):
    id: int
    user_id: int
    name: str
    color: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
