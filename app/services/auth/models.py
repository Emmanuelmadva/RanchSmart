from sqlalchemy import Column, Integer, String, Boolean
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String, nullable=False)
    profile_image = Column(String(255), nullable=True)  # Photo de profil
    is_active = Column(Boolean, default=True)

