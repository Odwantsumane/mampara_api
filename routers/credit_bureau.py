import hashlib

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud.credit_bureau as credit_bureau_crud
from db import get_db
from schemas import CreditCheckRequest
from serializers import credit_score_to_dict

router = APIRouter(prefix="/api/credit-bureau", tags=["credit-bureau"])


@router.post("/check")
def run_credit_check(payload: CreditCheckRequest, db: Session = Depends(get_db)):
    try:
        result = credit_bureau_crud.run_bureau_lookup(payload.name, payload.idNumber, payload.bureau)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not reach the credit bureau. Please try again.")

    borrower = credit_bureau_crud.find_borrower_by_id_number(db, payload.idNumber)
    record = credit_bureau_crud.save_credit_score(
        db,
        borrower_id=borrower.id if borrower else None,
        name=payload.name,
        id_number=payload.idNumber,
        bureau=payload.bureau,
        result=result,
    )
    return credit_score_to_dict(record)


@router.get("/latest")
def get_latest_credit_check(borrowerId: str, db: Session = Depends(get_db)):
    record = credit_bureau_crud.get_latest_credit_score(db, borrowerId)
    return credit_score_to_dict(record) if record else None


def _mock_bureau_response(id_number: str) -> dict:
    """Stand-in for a real bureau's API — a deterministic score derived from
    the ID number, so the same person always gets the same result. Point
    constants.CREDIT_BUREAU_API_URL at a real bureau's endpoint to replace
    this; that bureau's response shape will need mapping to match below."""
    digest = hashlib.sha256((id_number or "unknown").encode()).hexdigest()
    score = 300 + (int(digest[:8], 16) % 700)  # 300-999

    if score >= 700:
        risk_label, affordability = "Low Risk", "Approved (R 350/pay-cycle headroom)"
    elif score >= 500:
        risk_label, affordability = "Medium Risk", "Approved (R 150/pay-cycle headroom)"
    else:
        risk_label, affordability = "High Risk", "Declined (Insufficient headroom)"

    facilities = 1 + (int(digest[8:10], 16) % 4)
    exposure = facilities * 240
    recommended_max = min(1000, max(200, round((score - 300) * (1000 / 700) / 50) * 50))

    return {
        "score": score,
        "scoreScaleLabel": "Scale: 0 - 999",
        "riskLabel": risk_label,
        "defaultJudgements": "None Recorded" if score >= 500 else "1 Recorded",
        "openFacilities": f"{facilities} Active Account{'s' if facilities != 1 else ''} (R {exposure} exposure)",
        "affordability": affordability,
        "recommendedMaxAdvance": f"R {recommended_max:,.2f}",
    }


@router.post("/mock-lookup")
def mock_bureau_lookup(payload: CreditCheckRequest):
    return _mock_bureau_response(payload.idNumber)
