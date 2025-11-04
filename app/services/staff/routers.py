from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil, os

from database.connection import get_db
from app.services.staff import models, schemas
from app.services.animals.models import Animal

UPLOAD_DIR = "app/static/assets/staff_profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)

staff_router = APIRouter(prefix="/staff", tags=["Staff"])

# ----------------------
# CRUD Staff
# ----------------------

@staff_router.post("/", response_model=schemas.StaffRead)
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    new_staff = models.Staff(**staff.dict())
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff

@staff_router.get("/", response_model=List[schemas.StaffRead])
def get_all_staff(db: Session = Depends(get_db)):
    return db.query(models.Staff).all()

@staff_router.get("/{staff_id}", response_model=schemas.StaffRead)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    return staff

@staff_router.put("/{staff_id}", response_model=schemas.StaffRead)
def update_staff(staff_id: int, staff_update: schemas.StaffUpdate, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    for key, value in staff_update.dict(exclude_unset=True).items():
        setattr(staff, key, value)

    db.commit()
    db.refresh(staff)
    return staff

@staff_router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    db.delete(staff)
    db.commit()
    return {"detail": "Employé supprimé avec succès"}

# ----------------------
# Assignation d'un animal à un employé
# ----------------------
@staff_router.post("/{staff_id}/assign-animal/{animal_id}")
def assign_animal(staff_id: int, animal_id: int, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")

    animal.assigned_staff = staff
    db.commit()
    return {"detail": f"Animal {animal.name} assigné à {staff.name}"}

# ----------------------
# Upload d'une photo de profil
# ----------------------
@staff_router.post("/{staff_id}/upload-profile")
def upload_profile(staff_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    file_location = os.path.join(UPLOAD_DIR, f"{staff_id}_{file.filename}")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    staff.profile_image = file_location
    db.commit()
    db.refresh(staff)

    return {"detail": "Photo de profil uploadée avec succès", "file_path": file_location}
