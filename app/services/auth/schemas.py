from pydantic import BaseModel, EmailStr
from typing import Optional

# --- Schéma pour la création d'un employé ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # rôle de l'employé : cowboy, vet, manager...
    profile_image: Optional[str] = None  # chemin ou URL facultatif

# --- Schéma pour la lecture d'un employé ---
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    profile_image: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True
