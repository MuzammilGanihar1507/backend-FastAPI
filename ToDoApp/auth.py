import os

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: Optional[str]
    password: str

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    expire_time = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    payload = {"sub": username, "id": user_id, "exp": expire_time}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/create/user")
async def create_user(user_data: CreateUser, db: Session = Depends(get_db)):
    user_data_model = models.Users()
    user_data_model.email_id = user_data.email
    user_data_model.username = user_data.username
    user_data_model.first_name = user_data.first_name
    user_data_model.last_name = user_data.last_name

    hashed_password = get_password_hash(user_data.password)

    user_data_model.hashed_password = hashed_password
    user_data_model.is_active = True

    db.add(user_data_model)
    db.commit()

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    token_expires = timedelta(minutes=15)
    token = create_access_token(user.username, user.id, expires_delta= token_expires)
    return {"token": token}