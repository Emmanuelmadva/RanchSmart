from pydantic import BaseModel
from typing import Optional, List

class StaffCreate(BaseModel):
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    profile_image: Optional[str] = None

class StaffRead(StaffCreate):
    id: int
    assigned_animals: Optional[List[int]] = []

    class Config:
        orm_mode = True

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
