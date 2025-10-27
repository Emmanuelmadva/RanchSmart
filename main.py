from database.connection import Base, engine
from fastapi import FastAPI
from app.services.animals.models import Animal
from app.services.animals.routers import animal_router

print("Création des tables...")
Base.metadata.create_all(bind=engine)
print("Tables créées avec succès !")

app = FastAPI(title="RanchSmart API")

# Ajouter le router animals
app.include_router(animal_router, prefix="/animals", tags=["Animals"])