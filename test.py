from database.connection import Base, engine, SessionLocal
from app.services.animals.models import Animal

# Crée toutes les tables définies dans les modèles
print("🔧 Création des tables…")
Base.metadata.create_all(bind=engine)
print(" Tables créées avec succès !")
