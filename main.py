from database.connection import Base, engine
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.services.enclosures.maps.generate_map import generate_map
import os
from fastapi.middleware.cors import CORSMiddleware





from app.services.animals.models import Animal
from app.services.auth.models import User
from app.services.enclosures.models import Enclosure
from app.services.staff.models import Staff

from app.services.animals.routers import animal_router
from app.services.auth.routers import auth_router
from app.services.enclosures.routers import enclosure_router
from app.services.staff.routers import staff_router

app = FastAPI(title="RanchSmart API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ranchsmart-1.onrender.com"],  # ton frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Création des tables ---
def create_db_tables():
    print("Création des tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables OK !")
    except Exception as e:
        print(f"Erreur BDD : {e}")

create_db_tables()

STATIC_DIR = Path(__file__).parent / "app" / "static"  # ABSOLU
ASSETS_DIR = STATIC_DIR / "assets"
DASHBOARD_DIR = STATIC_DIR / "template" / "pages" / "dashboardUser"
ANIMALS_DIR = ASSETS_DIR / "animals"
STAFF_IMG_DIR = ASSETS_DIR / "staff_profiles"

os.makedirs(ANIMALS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/dashboardUser", StaticFiles(directory=DASHBOARD_DIR), name="dashboard")  # OK

@app.get("/", response_class=HTMLResponse)
def landing_page():
    file_path = STATIC_DIR / "template" / "pages" / "landing" / "landing.html"
    try:
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(content=f"<h1>404</h1><p>Fichier non trouvé : {file_path}</p>", status_code=404)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_index():
    file_path = DASHBOARD_DIR / "index.html"
    try:
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>index.html non trouvé</p>", status_code=404)

@app.get("/dashboard/animaux", response_class=HTMLResponse)
def dashboard_animals():
    file_path = DASHBOARD_DIR / "cards.html"
    try:
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>cards.html non trouvé</p>", status_code=404)

@app.get("/dashboard/enclos", response_class=HTMLResponse)
def dashboard_enclos():
    file_path = DASHBOARD_DIR / "enclos.html"
    try:
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>enclos.html non trouvé</p>", status_code=404)

@app.get("/dashboard/staff", response_class=HTMLResponse)
def dashboard_staff():
    file_path = DASHBOARD_DIR / "staff.html"  # <-- Corrigé
    try:
        return HTMLResponse(content=file_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404</h1><p>staff.html non trouvé</p>", status_code=404)

@app.get("/map", response_class=HTMLResponse)
def get_map():
    map_path = generate_map()  # génère et retourne le chemin du fichier HTML de la carte
    with open(map_path, "r", encoding="utf-8") as f:
        map_html = f.read()
    return HTMLResponse(content=map_html)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(animal_router, prefix="/animals", tags=["Animaux"])
app.include_router(enclosure_router, prefix="/enclosures", tags=["Enclos"])
app.include_router(staff_router, prefix="/staff", tags=["Staff"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)