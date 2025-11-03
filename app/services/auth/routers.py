from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.services.auth import models, schemas
from database.connection import get_db
from app.services.auth.schemas import LoginSchema
import shutil
import os

UPLOAD_DIR = "app/static/assets/profiles"
SECRET_KEY = "ranchsmart-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_router = APIRouter()

def hash_password(password: str) -> str:
    password = password[:72]  # tronque si trop long
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Inscription ---
@auth_router.post("/register", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

    hashed_pw = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role,
        profile_image=user.profile_image
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- Connexion ---
@auth_router.post("/login")
def login(login: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login.email).first()
    if not user or not verify_password(login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# --- Upload de la photo de profil ---
@auth_router.post("/upload-profile/{user_id}")
def upload_profile_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{user_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.profile_image = f"/{file_path}"
    db.commit()
    db.refresh(user)
    return {"detail": "Image de profil mise à jour", "profile_image": user.profile_image}
