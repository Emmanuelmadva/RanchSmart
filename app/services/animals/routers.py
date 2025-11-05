from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form 
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import re
import uuid
import shutil, os
from pathlib import Path
from database.connection import SessionLocal
from app.services.animals import models, schemas
from database.connection import get_db

animal_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@animal_router.get("/", response_model=List[schemas.AnimalRead])
def get_animals(db: Session = Depends(get_db)):
    return db.query(models.Animal).all()


@animal_router.get("/{animal_id}", response_model=schemas.AnimalRead)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    return animal

UPLOAD_DIR = Path("app/static/assets/animals")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@animal_router.post("/", response_model=schemas.AnimalRead)
async def create_animal_with_photo(
    name: str = Form(...),
    species: str = Form(...),
    age: int | None = Form(None),
    weight: float | None = Form(None),
    health_status: str = Form("Bonne santé"),
    last_vaccination: str | None = Form(None),  
    enclosure_id: int | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    parsed_date = None
    if last_vaccination:
        try:
            parsed_date = date.fromisoformat(last_vaccination)
        except ValueError:
            raise HTTPException(400, "Format de date invalide (YYYY-MM-DD)")

    new_animal = models.Animal(
        name=name,
        species=species,
        age=age,
        weight=weight,
        health_status=health_status,
        last_vaccination=parsed_date,
        enclosure_id=enclosure_id
    )

    if file and file.filename:
        clean_name = re.sub(r'[^\w\s-]', '_', name).strip().lower()
        clean_name = re.sub(r'\s+', '_', clean_name)[:30]
        ext = Path(file.filename).suffix.lower()
        if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
            ext = '.jpg'
        unique_id = uuid.uuid4().hex[:8]
        safe_filename = f"{clean_name}_{unique_id}{ext}"
        file_path = UPLOAD_DIR / safe_filename
        relative_path = f"/static/assets/animals/{safe_filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_animal.profile_image = relative_path

    db.add(new_animal)
    db.commit()
    db.refresh(new_animal)
    return new_animal

# Mettre à jour un animal existant et son enclos
@animal_router.put("/{animal_id}", response_model=schemas.AnimalRead)
def update_animal(animal_id: int, animal_update: schemas.AnimalUpdate, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")

    update_data = animal_update.dict(exclude_unset=True)

    # Vérifier l'enclos si on souhaite le changer
    if "enclosure_id" in update_data:
        if update_data["enclosure_id"]:
            enclosure = db.query(models.Enclosure).filter(models.Enclosure.id == update_data["enclosure_id"]).first()
            if not enclosure:
                raise HTTPException(status_code=404, detail="Enclos non trouvé")

    for key, value in update_data.items():
        setattr(animal, key, value)

    db.commit()
    db.refresh(animal)
    return animal


# Supprimer un animal
@animal_router.delete("/{animal_id}")
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")

    db.delete(animal)
    db.commit()
    return {"detail": "Animal supprimé avec succès"}


# Rechercher un animal par nom
@animal_router.get("/search/", response_model=List[schemas.AnimalRead])
def search_animals(name: str, db: Session = Depends(get_db)):
    results = db.query(models.Animal).filter(models.Animal.name.ilike(f"%{name}%")).all()
    if not results:
        raise HTTPException(status_code=404, detail="Aucun animal trouvé pour ce nom")
    return results


# Filtrer les animaux par critères
@animal_router.get("/filter/", response_model=List[schemas.AnimalRead])
def filter_animals(
        species: str | None = None,
        age: int | None = None,
        sex: str | None = None,
        enclosure_id: int | None = None,  # Filtrer par enclos
        db: Session = Depends(get_db)
):
    query = db.query(models.Animal)

    if species:
        query = query.filter(models.Animal.species == species)
    if age:
        query = query.filter(models.Animal.age == age)
    if sex:
        query = query.filter(models.Animal.sex == sex)
    if enclosure_id:
        query = query.filter(models.Animal.enclosure_id == enclosure_id)

    results = query.all()
    if not results:
        raise HTTPException(status_code=404, detail="Aucun animal trouvé avec ces critères")
    return results


# mettre a jour la photo de l'annimal
@animal_router.post("/{animal_id}/upload-photo")
def upload_animal_photo(animal_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    UPLOAD_DIR = Path(__file__).parent.parent.parent / "app" / "static" / "assets" / "animals"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{animal_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    animal.profile_image = f"/{file_path}"
    db.commit()
    db.refresh(animal)

    return {"detail": "Photo de l'animal enregistrée", "profile_image": animal.profile_image} 