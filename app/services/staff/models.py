from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from app.services.animals.models import Animal

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(50), nullable=False)  # cowboy, vet, caretaker, admin
    phone = Column(String(20), nullable=True)
    profile_image = Column(String, nullable=True)  # chemin vers image optionnelle

    # Relation avec les animaux assignés
    assigned_animals = relationship("Animal", back_populates="assigned_staff")
