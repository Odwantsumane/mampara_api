import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas import AdvanceDecisionRequest, CreateAdvanceRequest
from serializers import advance_to_dict
from utils import next_advance_id

router = APIRouter(prefix="/api/advances", tags=["advances"])


@router.get("")
def get_advance_book(profileType: str, borrowerName: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Advance)
    if profileType == "borrower" and borrowerName:
        query = query.filter(models.Advance.borrower == borrowerName)
    rows = query.order_by(models.Advance.sortOrder.asc()).all()
    return [advance_to_dict(row) for row in rows]


@router.post("")
def create_advance_application(payload: CreateAdvanceRequest, db: Session = Depends(get_db)):
    fee = round(payload.principal * (payload.feePercent / 100), 2)
    advance = models.Advance(
        id=next_advance_id(),
        borrower=payload.borrowerName,
        principal=f"R {payload.principal:,.2f}",
        fee=f"{payload.feePercent:g}% (R {fee:,.2f})",
        due=f"Due in {payload.termDays} days",
        status="Pending Approval",
        statusIcon="bi-hourglass-split",
        statusClass="secondary",
        # newer advances sort first, same as the old mock's list.insert(0, ...)
        sortOrder=-int(time.time() * 1000),
    )
    db.add(advance)
    db.commit()
    db.refresh(advance)
    return advance_to_dict(advance)


def _find_advance(db: Session, advance_id: str) -> models.Advance:
    row = db.query(models.Advance).filter(models.Advance.id == advance_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Advance not found.")
    return row


# advance ids look like "#ADV-2026-892" — the "#" makes them unsafe as a raw
# URL path segment (browsers treat it as a fragment delimiter), so the id is
# passed in the request body instead of the path.
@router.post("/approve")
def approve_advance(payload: AdvanceDecisionRequest, db: Session = Depends(get_db)):
    row = _find_advance(db, payload.id)
    row.status = "Performing"
    row.statusIcon = "bi-check-circle-fill"
    row.statusClass = "success"
    db.commit()
    db.refresh(row)
    return advance_to_dict(row)


@router.post("/decline")
def decline_advance(payload: AdvanceDecisionRequest, db: Session = Depends(get_db)):
    row = _find_advance(db, payload.id)
    row.status = "Declined"
    row.statusIcon = "bi-x-circle-fill"
    row.statusClass = "danger"
    db.commit()
    db.refresh(row)
    return advance_to_dict(row)
