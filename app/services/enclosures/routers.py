from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.services.enclosures import models, schemas
from database.connection import get_db

enclosure_router = APIRouter(prefix="/enclosures", tags=["Enclos"])

# Créer un enclos
@enclosure_router.post("/", response_model=schemas.EnclosureRead)
def create_enclosure(enclosure: schemas.EnclosureCreate, db: Session = Depends(get_db)):
    new_enclosure = models.Enclosure(**enclosure.dict())
    db.add(new_enclosure)
    db.commit()
    db.refresh(new_enclosure)
    return new_enclosure

# Lister tous les enclos
@enclosure_router.get("/", response_model=List[schemas.EnclosureRead])
def get_enclosures(db: Session = Depends(get_db)):
    return db.query(models.Enclosure).all()

# Récupérer un enclos par ID
@enclosure_router.get("/{enclosure_id}", response_model=schemas.EnclosureRead)
def get_enclosure(enclosure_id: int, db: Session = Depends(get_db)):
    enclosure = db.query(models.Enclosure).filter(models.Enclosure.id == enclosure_id).first()
    if not enclosure:
        raise HTTPException(status_code=404, detail="Enclos non trouvé")
    return enclosure

# Mettre à jour un enclos
@enclosure_router.put("/{enclosure_id}", response_model=schemas.EnclosureRead)
def update_enclosure(enclosure_id: int, enclosure_update: schemas.EnclosureUpdate, db: Session = Depends(get_db)):
    enclosure = db.query(models.Enclosure).filter(models.Enclosure.id == enclosure_id).first()
    if not enclosure:
        raise HTTPException(status_code=404, detail="Enclos non trouvé")

    for key, value in enclosure_update.dict(exclude_unset=True).items():
        setattr(enclosure, key, value)

    db.commit()
    db.refresh(enclosure)
    return enclosure

# Supprimer un enclos
@enclosure_router.delete("/{enclosure_id}")
def delete_enclosure(enclosure_id: int, db: Session = Depends(get_db)):
    enclosure = db.query(models.Enclosure).filter(models.Enclosure.id == enclosure_id).first()
    if not enclosure:
        raise HTTPException(status_code=404, detail="Enclos non trouvé")

    db.delete(enclosure)
    db.commit()
    return {"detail": "Enclos supprimé avec succès"}
