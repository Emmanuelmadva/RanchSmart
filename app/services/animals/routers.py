from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.connection import SessionLocal
from app.services.animals import models, schemas

animal_router = APIRouter()


# Dépendance pour récupérer la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Endpoints CRUD pour Animals
# ----------------------------

# Lister tous les animaux
@animal_router.get("/", response_model=List[schemas.AnimalRead])
def get_animals(db: Session = Depends(get_db)):
    return db.query(models.Animal).all()


# Récupérer un animal par ID
@animal_router.get("/{animal_id}", response_model=schemas.AnimalRead)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    return animal


# Ajouter un nouvel animal
@animal_router.post("/", response_model=schemas.AnimalRead)
def create_animal(animal: schemas.AnimalCreate, db: Session = Depends(get_db)):
    new_animal = models.Animal(**animal.dict())
    db.add(new_animal)
    db.commit()
    db.refresh(new_animal)
    return new_animal


# Mettre à jour un animal existant
@animal_router.put("/{animal_id}", response_model=schemas.AnimalRead)
def update_animal(animal_id: int, animal_update: schemas.AnimalUpdate, db: Session = Depends(get_db)):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")

    for key, value in animal_update.dict(exclude_unset=True).items():
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
