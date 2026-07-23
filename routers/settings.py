from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud.settings as settings_crud
from db import get_db
from schemas import UpdateSettingsRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _to_dict(row) -> dict:
    return {"advanceFeePercent": row.advanceFeePercent, "universalAdvanceLimit": row.universalAdvanceLimit}


@router.get("")
def get_settings(db: Session = Depends(get_db)):
    return _to_dict(settings_crud.get_settings(db))


@router.patch("")
def update_settings(payload: UpdateSettingsRequest, db: Session = Depends(get_db)):
    row = settings_crud.update_settings(db, payload.advanceFeePercent, payload.universalAdvanceLimit)
    return _to_dict(row)
