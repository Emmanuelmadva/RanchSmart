from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    profile_image: Optional[str] = None  # chemin ou URL

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_image: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
