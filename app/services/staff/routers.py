from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import shutil
from uuid import uuid4
from pathlib import Path
from database.connection import SessionLocal

from database.connection import get_db
from app.services.staff import models, schemas
from app.services.animals.models import Animal

# --- CONFIG ---
UPLOAD_DIR = Path("app/static/assets/staff_profiles")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- ROUTER ---
staff_router = APIRouter()

# --- DÉPENDANCE DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------
# CREATE - Avec upload image
# ----------------------
@staff_router.post("/", response_model=schemas.StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    phone: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
    
):
    # Vérifier unicité email
    if db.query(models.Staff).filter(models.Staff.email == email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    profile_image = None
    if file and file.filename:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Format d'image non supporté")

        filename = f"{uuid4().hex}{suffix}"
        file_path = UPLOAD_DIR / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        profile_image = f"/static/assets/staff_profiles/{filename}"

    new_staff = models.Staff(
        name=name,
        email=email,
        role=role,
        phone=phone,
        profile_image=profile_image
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff


# ----------------------
# READ - Tous les staffs
# ----------------------
@staff_router.get("/", response_model=List[schemas.StaffRead])
def get_all_staff(db: Session = Depends(get_db)):
    staffs = db.query(models.Staff).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "role": s.role,
            "phone": s.phone,
            "profile_image": s.profile_image,
            "assigned_animals": [a.id for a in s.assigned_animals]
        }
        for s in staffs
    ]

# ----------------------
# READ - Un staff
# ----------------------
@staff_router.get("/{staff_id}", response_model=schemas.StaffRead)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    return staff


# ----------------------
# UPDATE - Avec changement image
# ----------------------
@staff_router.put("/{staff_id}", response_model=schemas.StaffRead)
def update_staff(
    staff_id: int,
    name: str = Form(None),
    email: str = Form(None),
    role: str = Form(None),
    phone: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    # Vérifier email unique (sauf pour lui-même)
    if email and email != staff.email:
        if db.query(models.Staff).filter(models.Staff.email == email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Mise à jour des champs
    if name: staff.name = name
    if email: staff.email = email
    if role: staff.role = role
    if phone is not None: staff.phone = phone

    # Gestion de l'image
    if file and file.filename:
        # Supprimer l'ancienne image
        if staff.profile_image:
            old_path = Path("app") / staff.profile_image.lstrip("/")
            if old_path.exists():
                old_path.unlink()

        # Sauvegarder la nouvelle
        suffix = Path(file.filename).suffix.lower()
        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Format non supporté")

        filename = f"{uuid4().hex}{suffix}"
        file_path = UPLOAD_DIR / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        staff.profile_image = f"/static/assets/staff_profiles/{filename}"

    db.commit()
    db.refresh(staff)
    return staff


# ----------------------
# DELETE - Avec suppression image
# ----------------------
@staff_router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    # Supprimer l'image
    if staff.profile_image:
        img_path = Path("app") / staff.profile_image.lstrip("/")
        if img_path.exists():
            img_path.unlink()

    db.delete(staff)
    db.commit()
    return JSONResponse(status_code=204)


# ----------------------
# ASSIGN ANIMAL
# ----------------------
@staff_router.post("/{staff_id}/assign-animal/{animal_id}")
def assign_animal(staff_id: int, animal_id: int,db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")

    # Empêcher double assignation
    if animal.assigned_staff == staff_id:
        return {"detail": f"Animal {animal.name} déjà assigné à {staff.name}"}

    animal.assigned_staff = staff
    db.commit()
    return {"detail": f"Animal {animal.name} assigné à {staff.name}"}