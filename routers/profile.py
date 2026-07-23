from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud.users as users_crud
from auth.userAuthentication import hash_password, verify_password
from db import get_db
from schemas import ChangePasswordRequest, UpdateProfileRequest
from serializers import user_to_dict

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.patch("")
def update_profile(payload: UpdateProfileRequest, db: Session = Depends(get_db)):
    user = users_crud.update_user(db, payload.userId, payload.fields)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user_to_dict(user)


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = users_crud.get_user_by_id(db, payload.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not verify_password(payload.currentPassword, user.password):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    users_crud.change_password(db, payload.userId, hash_password(payload.newPassword))
    return {"ok": True}
