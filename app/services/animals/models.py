from sqlalchemy import Column, Integer, String, Float, Date
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
