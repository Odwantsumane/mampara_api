from fastapi import APIRouter

import store
from schemas import UpdateSettingsRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def get_settings():
    return store.settings


@router.patch("")
def update_settings(payload: UpdateSettingsRequest):
    store.settings["advanceFeePercent"] = payload.advanceFeePercent
    return store.settings
