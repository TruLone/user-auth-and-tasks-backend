from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskFileResponse(BaseModel):
    id: int
    original_name: str

    class Config:
        from_attributes = True

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    attachments: list[TaskFileResponse] = []

    class Config:
        from_attributes = True