from pydantic import BaseModel
from typing import Optional, List


class StaffCreate(BaseModel):
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    profile_image: Optional[str] = None

  

class StaffRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    assigned_animals: List[int] = []

    class Config:
        orm_mode = True
        from_attributes = True  # Pydantic v2

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
