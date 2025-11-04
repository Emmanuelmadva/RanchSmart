from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form 
from sqlalchemy.orm import Session
from typing import List
from datetime import date

import shutil, os

from database.connection import SessionLocal
from app.services.animals import models, schemas

animal_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "app/static/assets/animal_photos"
@animal_router.get("/", response_model=List[schemas.AnimalRead])
def get_animals(db: Session = Depends(get_db)):
    return db.query(models.Animal).all()


@animal_router.get("/{animal_id}", response_model=schemas.AnimalRead)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    return animal


@animal_router.post("/", response_model=schemas.AnimalRead)
def create_animal_with_photo(
    name: str = Form(...), 
    species: str = Form(...), 
    age: int | None = Form(None), 
    weight: float | None = Form(None), 
    health_status: str | None = Form("Bonne santé"), 
    last_vaccination: date | None = Form(None), 
    enclosure_id: int | None = Form(None), 
    file: UploadFile | None = File(None), 
    db: Session = Depends(get_db)
):
    if last_vaccination and isinstance(last_vaccination, str):
        try:
            last_vaccination = date.fromisoformat(last_vaccination)
        except ValueError:
             raise HTTPException(status_code=400, detail="Format de date de vaccination invalide. Utilisez YYYY-MM-DD.")
             
    if enclosure_id:
        try:
            enclosure = db.query(models.Enclosure).filter(models.Enclosure.id == enclosure_id).first()
        except AttributeError:
             pass
        
        if 'enclosure' in locals() and not enclosure: # Vérifie si la requête DB a été faite et si l'enclos est null
             raise HTTPException(status_code=404, detail=f"Enclos avec ID {enclosure_id} non trouvé")

    new_animal = models.Animal(
        name=name,
        species=species,
        age=age,
        weight=weight,
        health_status=health_status,
        last_vaccination=last_vaccination,
        enclosure_id=enclosure_id
    )

    # Sauvegarder la photo si fournie
    if file and file.filename:
        UPLOAD_DIR = "app/static/assets/animals"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{name.replace(' ', '_')}_{os.path.basename(file.filename)}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        relative_path = f"/static/assets/animals/{filename}" 
        
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

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{animal_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    animal.profile_image = f"/{file_path}"
    db.commit()
    db.refresh(animal)

    return {"detail": "Photo de l'animal enregistrée", "profile_image": animal.profile_image}