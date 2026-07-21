from fastapi import APIRouter, HTTPException

import store
from schemas import ChangePasswordRequest, UpdateProfileRequest

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.patch("")
def update_profile(payload: UpdateProfileRequest):
    user = store.find_user_by_id(payload.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.update(payload.fields)
    return store.to_public_user(user)


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest):
    user = store.find_user_by_id(payload.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user["password"] != payload.currentPassword:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    user["password"] = payload.newPassword
    return {"ok": True}
