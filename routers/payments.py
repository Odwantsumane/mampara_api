from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud.advances as advances_crud
import crud.payments as payments_crud
import crud.settings as settings_crud
import crud.users as users_crud
from db import get_db
from schemas import RequestPaymentRequest, UpdateBankDetailsRequest
from serializers import advance_to_dict, payment_to_dict
from utils import parse_currency, parse_fee_amount

router = APIRouter(prefix="/api/payments", tags=["payments"])

PAYABLE_STATUSES = {"Performing", "Late"}


@router.post("/request")
def request_payment(payload: RequestPaymentRequest, db: Session = Depends(get_db)):
    """Starts a manual EFT repayment — creates a Pending payment record and
    hands back the reference + bank details for the borrower to pay to
    directly. Nothing here confirms itself; an admin marks it received once
    the money actually lands (see /confirm)."""
    advance = advances_crud.get_advance_by_id(db, payload.advanceId)
    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found.")
    if advance.borrowerId != payload.borrowerId:
        raise HTTPException(status_code=403, detail="This advance does not belong to you.")
    if advance.status not in PAYABLE_STATUSES:
        raise HTTPException(status_code=400, detail="This advance isn't currently payable.")

    borrower = users_crud.get_user_by_id(db, payload.borrowerId)
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found.")

    amount = parse_currency(advance.principal) + parse_fee_amount(advance.fee)
    reference = payments_crud.new_reference()
    payment = payments_crud.create_pending_payment(
        db, reference=reference, advance_id=advance.id, borrower_id=borrower.id, amount=amount
    )

    settings_row = settings_crud.get_settings(db)
    return {
        "paymentId": payment.id,
        "reference": payment.reference,
        "amount": payment.amount,
        "bankName": settings_row.bankName,
        "accountHolderName": settings_row.accountHolderName,
        "accountNumber": settings_row.accountNumber,
        "branchCode": settings_row.branchCode,
    }


@router.post("/{payment_id}/confirm")
def confirm_payment(payment_id: str, db: Session = Depends(get_db)):
    """Admin action: marks a pending EFT as actually received in the real
    bank account, and settles the linked advance."""
    payment = payments_crud.confirm_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")
    advance = advances_crud.mark_advance_repaid(db, payment.advanceId)
    return {"payment": payment_to_dict(payment), "advance": advance_to_dict(advance) if advance else None}


@router.post("/{payment_id}/cancel")
def cancel_payment(payment_id: str, db: Session = Depends(get_db)):
    """Admin action: closes out a stale/incorrect pending request without
    touching the advance — the borrower can start a fresh Pay Now request."""
    payment = payments_crud.cancel_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return payment_to_dict(payment)


@router.get("")
def list_payments(db: Session = Depends(get_db)):
    """Payment log — the frontend only surfaces this in the admin-only
    Bank Payment Details panel, matching this app's existing convention of
    trusting the caller's profileType rather than enforcing it server-side."""
    result = []
    for payment in payments_crud.get_all_payments(db):
        borrower = users_crud.get_user_by_id(db, payment.borrowerId)
        result.append(payment_to_dict(payment, borrower_name=borrower.name if borrower else None))
    return result


@router.get("/bank-details")
def get_bank_details(db: Session = Depends(get_db)):
    """Admin-only editing view of the receiving bank account — deliberately
    a separate endpoint from GET /api/settings, which every signed-in user
    calls just for the fee/limit numbers."""
    settings_row = settings_crud.get_settings(db)
    return {
        "bankName": settings_row.bankName,
        "accountHolderName": settings_row.accountHolderName,
        "accountNumber": settings_row.accountNumber,
        "branchCode": settings_row.branchCode,
    }


@router.patch("/bank-details")
def update_bank_details(payload: UpdateBankDetailsRequest, db: Session = Depends(get_db)):
    row = settings_crud.update_bank_details(
        db, payload.bankName, payload.accountHolderName, payload.accountNumber, payload.branchCode
    )
    return {
        "bankName": row.bankName,
        "accountHolderName": row.accountHolderName,
        "accountNumber": row.accountNumber,
        "branchCode": row.branchCode,
    }
