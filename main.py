from database.connection import Base, engine
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles 

from app.services.animals.models import Animal
from app.services.auth.models import User 
from app.services.enclosures.models import Enclosure 
from app.services.staff.models import Staff 

from app.services.animals.routers import animal_router
from app.services.auth.routers import auth_router
from app.services.enclosures.routers import enclosure_router
from app.services.staff.routers import staff_router


app = FastAPI(title="RanchSmart API")

def create_db_tables():
    print("Tentative de création des tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables créées avec succès ou déjà existantes !")
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")

create_db_tables()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

HTML_FILE_PATH = Path("app") / "static" / "template" / "pages" / "landing" / "landing.html"

@app.get("/", response_class=HTMLResponse)
def landing_page():
    """Lit et renvoie le contenu du fichier HTML de la page d'accueil."""
    try:
        html_content = HTML_FILE_PATH.read_text(encoding="utf-8")
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content=f"<h1>Erreur 404</h1><p>Fichier HTML non trouvé au chemin: {HTML_FILE_PATH}</p>", status_code=404)


app.include_router(animal_router, prefix="/animals", tags=["Animals"])
app.include_router(auth_router, prefix="/auth", tags=["Authentification"])
app.include_router(enclosure_router, prefix="/enclosures", tags=["Enclos"])
app.include_router(staff_router, prefix="/staff", tags=["Staff"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)