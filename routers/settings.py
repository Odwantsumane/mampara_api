from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas import UpdateSettingsRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db)):
    row = db.query(models.PlatformSettings).filter(models.PlatformSettings.id == 1).first()
    return {"advanceFeePercent": row.advanceFeePercent}


@router.patch("")
def update_settings(payload: UpdateSettingsRequest, db: Session = Depends(get_db)):
    row = db.query(models.PlatformSettings).filter(models.PlatformSettings.id == 1).first()
    row.advanceFeePercent = payload.advanceFeePercent
    db.commit()
    return {"advanceFeePercent": row.advanceFeePercent}
