from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud.billing as billing_crud
from db import get_db
from schemas import AddPaymentMethodRequest, UpdatePaymentMethodRequest
from serializers import payment_method_to_dict

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("")
def get_billing(profileType: str, db: Session = Depends(get_db)):
    if billing_crud.get_billing_profile(db, profileType) is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    return {
        "paymentMethods": [payment_method_to_dict(m) for m in billing_crud.get_payment_methods(db, profileType)],
    }


@router.post("/payment-methods")
def add_payment_method(payload: AddPaymentMethodRequest, db: Session = Depends(get_db)):
    if billing_crud.get_billing_profile(db, payload.profileType) is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    method = billing_crud.add_payment_method(
        db, payload.profileType, payload.cardholderName, payload.cardNumber, payload.expiry, payload.debitDate
    )
    return payment_method_to_dict(method)


@router.patch("/payment-methods/{method_id}")
def update_payment_method(method_id: str, payload: UpdatePaymentMethodRequest, db: Session = Depends(get_db)):
    method = billing_crud.update_payment_method(
        db, method_id, payload.profileType, payload.cardholderName, payload.cardNumber, payload.expiry, payload.debitDate
    )
    if method is None:
        raise HTTPException(status_code=404, detail="Payment method not found.")
    return payment_method_to_dict(method)


@router.delete("/payment-methods/{method_id}")
def remove_payment_method(method_id: str, profileType: str, db: Session = Depends(get_db)):
    billing_crud.remove_payment_method(db, method_id, profileType)
    return {"ok": True}
