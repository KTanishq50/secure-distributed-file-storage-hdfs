from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

from app.db.session import get_db
from app.db.models import User
from app.core.auth import hash_password, verify, create_token

router = APIRouter()


@router.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("student"),
    db: Session = Depends(get_db)
):
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(400, "User already exists")

    user = User(
        username=username,
        password_hash=hash_password(password),
        encryption_key=Fernet.generate_key().decode(),
        role=role
    )

    db.add(user)
    db.commit()

    return {"msg": "registered"}


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(username=username).first()

    if not user or not verify(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user.id, user.role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }