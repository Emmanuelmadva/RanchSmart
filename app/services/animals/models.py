from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    health_status = Column(String, default="Healthy")
    last_vaccination = Column(Date, nullable=True)
    profile_image = Column(String, nullable=True)

    # Clé étrangère vers l'enclos
    enclosure_id = Column(Integer, ForeignKey("enclosures.id"), nullable=True)

    # Relation avec l'enclos
    enclosure = relationship("Enclosure", back_populates="animals")

    # Ajouter à Animal
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    assigned_staff = relationship("Staff", back_populates="assigned_animals")