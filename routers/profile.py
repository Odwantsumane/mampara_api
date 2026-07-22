from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas import ChangePasswordRequest, UpdateProfileRequest
from serializers import user_to_dict

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Only these fields are ever editable from the Personal Information form —
# anything else in the payload's `fields` dict is ignored rather than blindly
# applied to the row.
EDITABLE_FIELDS = {"inputNames", "inputSurnames", "inputIdNumber", "inputPhone", "inputResidency"}


@router.patch("")
def update_profile(payload: UpdateProfileRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    for key, value in payload.fields.items():
        if key in EDITABLE_FIELDS:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user_to_dict(user)


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.password != payload.currentPassword:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    user.password = payload.newPassword
    db.commit()
    return {"ok": True}
