from database.connection import SessionLocal

from app.services.animals.models import Animal
from app.services.enclosures.models import Enclosure
from app.services.staff.models import Staff  
print("Connexion à la base de données...")

db = SessionLocal()

__all__ = [Animal, Enclosure, Staff]

# Trouve tous les animaux avec profile_image contenant des caractères suspects
corrupted = db.query(Animal).filter(
    Animal.profile_image.ilike('%ijks.%') |
    Animal.profile_image.ilike('%3B%') |
    Animal.profile_image.ilike('%;%') |
    Animal.profile_image.ilike('%25%')
).all()

print(f"{len(corrupted)} animaux avec image corrompue trouvés")

for animal in corrupted:
    old_path = animal.profile_image
    print(f"  ID {animal.id}: {old_path} → SUPPRIMÉ")
    animal.profile_image = None  # Réinitialise

db.commit()
db.close()
print("Nettoyage terminé ! Base de données propre.")