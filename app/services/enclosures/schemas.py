from pydantic import BaseModel
from typing import List, Optional
from app.services.animals.schemas import AnimalRead

class EnclosureBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    area: Optional[float] = None
    polygon_data: Optional[str] = None

class EnclosureCreate(EnclosureBase):
    pass

class EnclosureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area: Optional[float] = None
    polygon_data: Optional[str] = None

class EnclosureRead(EnclosureBase):
    id: int
    animals: List[AnimalRead] = []  # Liste des animaux assignés à l'enclos

    class Config:
        orm_mode = True
