from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud.advances as advances_crud
import crud.kyc as kyc_crud
import crud.settings as settings_crud
import crud.users as users_crud
from db import get_db
from schemas import AdvanceDecisionRequest, CreateAdvanceRequest
from serializers import advance_to_dict

router = APIRouter(prefix="/api/advances", tags=["advances"])


@router.get("")
def get_advance_book(profileType: str, borrowerId: str = "", db: Session = Depends(get_db)):
    rows = advances_crud.get_advance_book(db, profileType, borrowerId)
    return [advance_to_dict(row) for row in rows]


@router.post("")
def create_advance_application(payload: CreateAdvanceRequest, db: Session = Depends(get_db)):
    borrower = users_crud.get_user_by_id(db, payload.borrowerId)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found.")

    kyc_status = kyc_crud.get_kyc_completeness(db, payload.borrowerId)
    if not kyc_status["complete"]:
        raise HTTPException(
            status_code=403,
            detail="Your KYC documents must be fully uploaded and approved before requesting an advance.",
        )

    settings_row = settings_crud.get_settings(db)
    limit_info = advances_crud.get_borrower_limit_info(db, payload.borrowerId, settings_row.universalAdvanceLimit)
    if payload.principal > limit_info["availableLimit"]:
        raise HTTPException(
            status_code=403,
            detail=f"This exceeds your available advance limit of R {limit_info['availableLimit']:,.2f}.",
        )

    advance = advances_crud.create_advance(db, borrower, payload.principal, payload.feePercent, payload.termDays)
    return advance_to_dict(advance)


# advance ids look like "#ADV-2026-892" — the "#" makes them unsafe as a raw
# URL path segment (browsers treat it as a fragment delimiter), so the id is
# passed in the request body instead of the path.
@router.post("/approve")
def approve_advance(payload: AdvanceDecisionRequest, db: Session = Depends(get_db)):
    advance = advances_crud.approve_advance(db, payload.id)
    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found.")
    return advance_to_dict(advance)


@router.post("/decline")
def decline_advance(payload: AdvanceDecisionRequest, db: Session = Depends(get_db)):
    advance = advances_crud.decline_advance(db, payload.id)
    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found.")
    return advance_to_dict(advance)
