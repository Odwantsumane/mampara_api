from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "super-secret-of-secrets"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes=15):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def refresh(token):
    try:
        payload = jwt.decode(token.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            return {"access_token": None}

        new_access = create_access_token({"sub": payload["sub"]})
    except:
        return {"access_token": None}

    return {"access_token": new_access}

def authenticate(token):
    payload = jwt.decode(token.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

    if payload.get("type") != "refresh":
        return {"access_token": None}

    return {"access_token": payload["sub"]}

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return int(user_id)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )