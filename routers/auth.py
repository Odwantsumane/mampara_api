from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

import crud.users as users_crud
from auth.userAuthentication import create_access_token, decode_user_id, hash_password
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


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = users_crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = create_access_token({"sub": user.id})
    return {"token": token, "user": user_to_dict(user)}


@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if users_crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists.")

    name_parts = payload.name.strip().split(" ")
    first_name = name_parts[0] if name_parts and name_parts[0] else "New"
    surname = " ".join(name_parts[1:]) or "-"

    users_crud.create_user(
        db,
        email=payload.email,
        password=hash_password(payload.password),
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
    return login(LoginRequest(email=payload.email, password=payload.password), db)


@router.post("/logout")
def logout():
    # Stateless JWTs — nothing server-side to invalidate. The frontend just
    # discards its stored token.
    return {"ok": True}


@router.get("/me")
def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = _extract_token(authorization)
    if not token:
        return None
    user_id = decode_user_id(token)
    if not user_id:
        return None
    user = users_crud.get_user_by_id(db, user_id)
    return user_to_dict(user) if user else None
