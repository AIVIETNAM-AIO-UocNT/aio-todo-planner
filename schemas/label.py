from pydantic import BaseModel, ConfigDict
from typing import Optional 
from datetime import datetime

class LabelBase(BaseModel):
    name: str
    color: Optional[str] = None

class LabelCreate(LabelBase):
    pass

class LabelResponse(LabelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LabelUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None