from pydantic import BaseModel
from typing import Optional
from datetime import date

# Schéma pour la création d'un animal
class AnimalCreate(BaseModel):
    name: str
    species: str
    age: Optional[int] = None
    weight: Optional[float] = None
    health_status: Optional[str] = "Bonne santé"
    last_vaccination: Optional[date] = None

# Schéma pour la lecture d'un animal (avec l'id)
class AnimalRead(AnimalCreate):
    id: int

    class Config:
        orm_mode = True

# Schéma pour la mise à jour d'un animal
class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    health_status: Optional[str] = None
    last_vaccination: Optional[date] = None
