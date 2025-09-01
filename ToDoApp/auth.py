from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: Optional[str]
    password: str

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

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
    return 'User Validated!'