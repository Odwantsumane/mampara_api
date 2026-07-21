import time

from fastapi import APIRouter, Header, HTTPException

import store
from schemas import LoginRequest, SignupRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization[7:]
    return authorization


@router.post("/login")
def login(payload: LoginRequest):
    user = store.find_user_by_email(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = store.make_token(user["id"])
    store.sessions[token] = user["id"]
    return {"token": token, "user": store.to_public_user(user)}


@router.post("/signup")
def signup(payload: SignupRequest):
    if store.find_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists.")

    name_parts = payload.name.strip().split(" ")
    first_name = name_parts[0] if name_parts and name_parts[0] else "New"
    surname = " ".join(name_parts[1:]) or "-"

    new_user = {
        "id": f"usr_{int(time.time() * 1000)}",
        "email": payload.email,
        "password": payload.password,
        "profileType": "borrower",
        "name": payload.name or "New Borrower",
        "role": "Borrower Account",
        "badgeIcon": "bi-person-check-fill",
        "badgeText": "New Borrower",
        "tier": "Starter Borrower Tier",
        "avatar": "https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=150&h=150&fit=crop&crop=faces",
        "inputNames": first_name,
        "inputSurnames": surname,
        "inputIdNumber": "",
        "inputPhone": payload.phone or "",
        "inputResidency": "",
    }
    store.users.append(new_user)
    return login(LoginRequest(email=payload.email, password=payload.password))


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)):
    token = _extract_token(authorization)
    if token:
        store.sessions.pop(token, None)
    return {"ok": True}


@router.get("/me")
def get_current_user(authorization: str | None = Header(default=None)):
    token = _extract_token(authorization)
    if not token:
        return None
    user_id = store.sessions.get(token)
    if not user_id:
        return None
    user = store.find_user_by_id(user_id)
    return store.to_public_user(user) if user else None
