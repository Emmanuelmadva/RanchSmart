from fastapi import FastAPI
from app.services.animals.routers import animal_router

app = FastAPI()
app.include_router(animal_router, prefix="/animals", tags=["Animals"])
