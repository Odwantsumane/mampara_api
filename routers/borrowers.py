from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud.advances as advances_crud
import crud.credit_bureau as credit_bureau_crud
import crud.kyc as kyc_crud
import crud.users as users_crud
from db import get_db

router = APIRouter(prefix="/api/borrowers", tags=["borrowers"])


def _kyc_status(completeness: dict) -> tuple[str, str]:
    if completeness["complete"]:
        return "Verified", "success"
    if completeness["rejectedCategories"]:
        return "Action Needed", "danger"
    if completeness["missingCategories"]:
        return "Incomplete", "secondary"
    return "Pending Review", "warning"


def _risk_tier(score: int | None) -> tuple[str, str]:
    if score is None:
        return "Unknown", "secondary"
    if score >= 700:
        return "Low", "success"
    if score >= 500:
        return "Medium", "warning"
    return "High", "danger"


@router.get("")
def get_borrower_directory(db: Session = Depends(get_db)):
    """Real, registered-borrower directory for the admin's Borrowers tab —
    KYC status, latest credit score, and active advance count, all derived
    from the KYC/credit-bureau/advances data actually on file."""
    result = []
    for borrower in users_crud.get_borrowers(db):
        completeness = kyc_crud.get_kyc_completeness(db, borrower.id)
        kyc_label, kyc_class = _kyc_status(completeness)

        credit = credit_bureau_crud.get_latest_credit_score(db, borrower.id)
        risk_label, risk_class = _risk_tier(credit.score if credit else None)

        result.append({
            "id": borrower.id,
            "name": borrower.name,
            "contact": borrower.inputPhone,
            "kycStatus": kyc_label,
            "kycClass": kyc_class,
            "creditScore": credit.score if credit else None,
            "riskTier": risk_label,
            "riskClass": risk_class,
            "activeAdvances": advances_crud.get_active_advance_count(db, borrower.id),
        })
    return result
