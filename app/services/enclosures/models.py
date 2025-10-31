from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class Enclosure(Base):
    __tablename__ = "enclosures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area = Column(Float, nullable=True)  # en hectares ou m²
    polygon_data = Column(Text, nullable=True)  # coordonnées du polygone (GeoJSON)

    # Relation bidirectionnelle avec Animal
    animals = relationship("Animal", back_populates="enclosure")
