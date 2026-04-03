# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    admin_key: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # for Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

class TimeEntryUpdate(BaseModel):
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None