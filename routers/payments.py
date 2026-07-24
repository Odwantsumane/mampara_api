import requests
from fastapi import APIRouter, Body, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

import constants
import crud.advances as advances_crud
import crud.payments as payments_crud
import crud.users as users_crud
from db import get_db
from schemas import InitializePaymentRequest
from serializers import advance_to_dict, payment_to_dict
from utils import parse_currency, parse_fee_amount

router = APIRouter(prefix="/api/payments", tags=["payments"])

PAYABLE_STATUSES = {"Performing", "Late"}


@router.post("/initialize")
def initialize_payment(payload: InitializePaymentRequest, db: Session = Depends(get_db)):
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
    callback_url = f"{constants.PAYSTACK_CALLBACK_URL}/?reference={reference}"

    try:
        result = payments_crud.initialize_transaction(borrower.email, amount, reference, callback_url)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not reach the payment gateway. Please try again.")

    authorization_url = result["data"]["authorization_url"]
    payments_crud.create_payment(
        db,
        reference=reference,
        advance_id=advance.id,
        borrower_id=borrower.id,
        amount=amount,
        authorization_url=authorization_url,
    )
    return {"authorizationUrl": authorization_url, "reference": reference}


@router.get("/verify")
def verify_payment(reference: str, db: Session = Depends(get_db)):
    payment = payments_crud.get_payment_by_reference(db, reference)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")

    try:
        result = payments_crud.verify_transaction(reference)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not reach the payment gateway. Please try again.")

    gateway_status = result["data"]["status"]  # "success" | "failed"
    advance = advances_crud.get_advance_by_id(db, payment.advanceId)
    if gateway_status == "success":
        payments_crud.mark_payment_status(db, reference, "Success")
        # keyed off the advance's own state (not payment.status) so calling
        # verify twice for the same reference is safe and idempotent
        if advance and advance.status != "Repaid":
            advance = advances_crud.mark_advance_repaid(db, payment.advanceId)
    else:
        payments_crud.mark_payment_status(db, reference, "Failed")
        advance = None

    return {
        "status": gateway_status,
        "reference": reference,
        "amount": payment.amount,
        "advance": advance_to_dict(advance) if advance else None,
    }


@router.get("")
def list_payments(db: Session = Depends(get_db)):
    """Payment log — the frontend only surfaces this in the admin-only
    Payment Gateway panel, matching this app's existing convention of
    trusting the caller's profileType rather than enforcing it server-side."""
    result = []
    for payment in payments_crud.get_all_payments(db):
        borrower = users_crud.get_user_by_id(db, payment.borrowerId)
        result.append(payment_to_dict(payment, borrower_name=borrower.name if borrower else None))
    return result


@router.get("/gateway-info")
def gateway_info():
    """Admin-only visibility into the configured gateway. Never returns the
    secret key — only the public key (safe to expose, as with any Paystack
    integration) and whether a real account has been configured."""
    return {
        "publicKey": constants.PAYSTACK_PUBLIC_KEY,
        "baseUrl": constants.PAYSTACK_BASE_URL,
        "configured": not constants.PAYSTACK_SECRET_KEY.startswith("sk_test_mock"),
    }


# --- Mock gateway -----------------------------------------------------------
# Stands in for Paystack's real API so advance repayment works out of the box
# in dev/demo. Mirrors Paystack's actual request/response shapes; point
# constants.PAYSTACK_BASE_URL at https://api.paystack.co with real keys to
# swap this out for the genuine service.

def _checkout_html(reference: str, amount: float) -> str:
    return f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Mock Payment Gateway</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; background: #0f1720; color: #e8ecf1;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
  .card {{ background: #1a2531; border-radius: 12px; padding: 32px; width: 360px; box-shadow: 0 10px 40px rgba(0,0,0,0.4); }}
  .badge {{ display: inline-block; font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
            background: #f59e0b22; color: #f59e0b; padding: 4px 10px; border-radius: 20px; margin-bottom: 16px; }}
  h1 {{ font-size: 18px; margin: 0 0 4px; }}
  .amount {{ font-size: 32px; font-weight: 700; margin: 16px 0; color: #22c55e; }}
  .ref {{ font-size: 12px; color: #8b98a5; margin-bottom: 24px; word-break: break-all; }}
  button {{ width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 15px; font-weight: 600;
            cursor: pointer; margin-bottom: 10px; }}
  .pay {{ background: #22c55e; color: #062b12; }}
  .cancel {{ background: transparent; color: #8b98a5; border: 1px solid #2b3947; }}
</style>
</head>
<body>
  <div class="card">
    <span class="badge">Test Mode — Mock Gateway</span>
    <h1>Advance Repayment</h1>
    <div class="amount">R {amount:,.2f}</div>
    <div class="ref">Reference: {reference}</div>
    <form method="post" action="/api/payments/mock-paystack/checkout/complete">
      <input type="hidden" name="reference" value="{reference}">
      <button type="submit" class="pay">Pay with Test Card</button>
    </form>
    <a href="/api/payments/mock-paystack/checkout/cancel?reference={reference}">
      <button type="button" class="cancel">Cancel</button>
    </a>
  </div>
</body>
</html>
"""


@router.post("/mock-paystack/transaction/initialize")
def mock_initialize_transaction(payload: dict = Body(...)):
    reference = payload.get("reference") or payments_crud.new_reference()
    return {
        "status": True,
        "message": "Authorization URL created",
        "data": {
            "authorization_url": f"{constants.PAYSTACK_BASE_URL}/checkout?reference={reference}",
            "access_code": reference,
            "reference": reference,
        },
    }


@router.get("/mock-paystack/transaction/verify/{reference}")
def mock_verify_transaction(reference: str, db: Session = Depends(get_db)):
    payment = payments_crud.get_payment_by_reference(db, reference)
    if not payment:
        raise HTTPException(status_code=404, detail="Unknown reference.")
    gateway_status = "success" if payment.status == "Success" else "failed"
    return {
        "status": True,
        "data": {"status": gateway_status, "reference": reference, "amount": round(payment.amount * 100)},
    }


@router.get("/mock-paystack/checkout", response_class=HTMLResponse)
def mock_checkout_page(reference: str, db: Session = Depends(get_db)):
    payment = payments_crud.get_payment_by_reference(db, reference)
    if not payment:
        return HTMLResponse("<h3>Unknown payment reference.</h3>", status_code=404)
    return HTMLResponse(_checkout_html(reference, payment.amount))


@router.post("/mock-paystack/checkout/complete")
def mock_checkout_complete(reference: str = Form(...), db: Session = Depends(get_db)):
    payment = payments_crud.mark_payment_status(db, reference, "Success")
    if not payment:
        raise HTTPException(status_code=404, detail="Unknown reference.")
    return RedirectResponse(f"{constants.PAYSTACK_CALLBACK_URL}/?reference={reference}&status=success", status_code=303)


@router.get("/mock-paystack/checkout/cancel")
def mock_checkout_cancel(reference: str, db: Session = Depends(get_db)):
    payments_crud.mark_payment_status(db, reference, "Failed")
    return RedirectResponse(f"{constants.PAYSTACK_CALLBACK_URL}/?reference={reference}&status=cancelled", status_code=303)
