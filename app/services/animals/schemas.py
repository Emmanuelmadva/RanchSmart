# app/services/animals/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class AnimalCreate(BaseModel):
    name: str
    species: str
    age: Optional[int] = None
    weight: Optional[float] = None
    health_status: Optional[str] = "Bonne santé"
    last_vaccination: Optional[date] = None
    enclosure_id: Optional[int] = None
    profile_image: Optional[str] = None  # Photo optionnelle

class AnimalRead(AnimalCreate):
    id: int


class Config:
    from_attributes = True


class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    health_status: Optional[str] = None
    last_vaccination: Optional[date] = None
    enclosure_id: Optional[int] = None
    profile_image: Optional[str] = None  # Permet de mettre à jour la photo


