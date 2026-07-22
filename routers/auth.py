import time

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import utils
from db import get_db
from schemas import LoginRequest, SignupRequest
from serializers import user_to_dict

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization[7:]
    return authorization


def _find_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(func.lower(models.User.email) == email.lower()).first()


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = _find_by_email(db, payload.email)
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = utils.make_token(user.id)
    db.add(models.Session(token=token, userId=user.id))
    db.commit()
    return {"token": token, "user": user_to_dict(user)}


@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if _find_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists.")

    name_parts = payload.name.strip().split(" ")
    first_name = name_parts[0] if name_parts and name_parts[0] else "New"
    surname = " ".join(name_parts[1:]) or "-"

    new_user = models.User(
        id=f"usr_{int(time.time() * 1000)}",
        email=payload.email,
        password=payload.password,
        profileType="borrower",
        name=payload.name or "New Borrower",
        role="Borrower Account",
        badgeIcon="bi-person-check-fill",
        badgeText="New Borrower",
        tier="Starter Borrower Tier",
        avatar="https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=150&h=150&fit=crop&crop=faces",
        inputNames=first_name,
        inputSurnames=surname,
        inputIdNumber="",
        inputPhone=payload.phone or "",
        inputResidency="",
    )
    db.add(new_user)
    db.commit()
    return login(LoginRequest(email=payload.email, password=payload.password), db)


@router.post("/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = _extract_token(authorization)
    if token:
        db.query(models.Session).filter(models.Session.token == token).delete()
        db.commit()
    return {"ok": True}


@router.get("/me")
def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = _extract_token(authorization)
    if not token:
        return None
    session = db.query(models.Session).filter(models.Session.token == token).first()
    if not session:
        return None
    user = db.query(models.User).filter(models.User.id == session.userId).first()
    return user_to_dict(user) if user else None
