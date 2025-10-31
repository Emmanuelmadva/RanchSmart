from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil, os

from database.connection import get_db
from app.services.staff import models, schemas
from app.services.animals.models import Animal

UPLOAD_DIR = "app/static/assets/staff_profiles"

staff_router = APIRouter(prefix="/staff", tags=["Staff"])

# Dépendance DB
def get_db_session():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# CRUD Staff
# ----------------------

@staff_router.post("/", response_model=schemas.StaffRead)
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db_session)):
    new_staff = models.Staff(**staff.dict())
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff

# Assignation d'un animal à un employé
@staff_router.post("/{staff_id}/assign-animal/{animal_id}")
def assign_animal(staff_id: int, animal_id: int, db: Session = Depends(get_db_session)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")

    animal.assigned_staff = staff
    db.commit()
    return {"detail": f"Animal {animal.name} assigné à {staff.name}"}
