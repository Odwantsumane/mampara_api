from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas import AddPaymentMethodRequest, UpdatePaymentMethodRequest
from serializers import invoice_to_dict, payment_method_to_dict
from utils import detect_card_brand, next_payment_method_id

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("")
def get_billing(profileType: str, db: Session = Depends(get_db)):
    profile = db.query(models.BillingProfile).filter(models.BillingProfile.profileType == profileType).first()
    if profile is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    methods = db.query(models.PaymentMethod).filter(models.PaymentMethod.profileType == profileType).all()
    invoices = db.query(models.Invoice).filter(models.Invoice.profileType == profileType).all()
    return {
        "planName": profile.planName,
        "planPrice": profile.planPrice,
        "renewsOn": profile.renewsOn,
        "paymentMethods": [payment_method_to_dict(m) for m in methods],
        "invoices": [invoice_to_dict(i) for i in invoices],
    }


@router.post("/payment-methods")
def add_payment_method(payload: AddPaymentMethodRequest, db: Session = Depends(get_db)):
    profile = db.query(models.BillingProfile).filter(models.BillingProfile.profileType == payload.profileType).first()
    if profile is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    existing_count = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.profileType == payload.profileType
    ).count()
    method = models.PaymentMethod(
        id=next_payment_method_id(),
        profileType=payload.profileType,
        type="card",
        brand=detect_card_brand(payload.cardNumber),
        last4=payload.cardNumber[-4:],
        cardNumber=payload.cardNumber,
        cardholderName=payload.cardholderName,
        expiry=payload.expiry,
        debitDate=payload.debitDate,
        isPrimary=existing_count == 0,
    )
    db.add(method)
    db.commit()
    db.refresh(method)
    return payment_method_to_dict(method)


@router.patch("/payment-methods/{method_id}")
def update_payment_method(method_id: str, payload: UpdatePaymentMethodRequest, db: Session = Depends(get_db)):
    method = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.id == method_id,
        models.PaymentMethod.profileType == payload.profileType,
    ).first()
    if method is None:
        raise HTTPException(status_code=404, detail="Payment method not found.")
    method.brand = detect_card_brand(payload.cardNumber)
    method.last4 = payload.cardNumber[-4:]
    method.cardNumber = payload.cardNumber
    method.cardholderName = payload.cardholderName
    method.expiry = payload.expiry
    method.debitDate = payload.debitDate
    db.commit()
    db.refresh(method)
    return payment_method_to_dict(method)


@router.delete("/payment-methods/{method_id}")
def remove_payment_method(method_id: str, profileType: str, db: Session = Depends(get_db)):
    db.query(models.PaymentMethod).filter(
        models.PaymentMethod.id == method_id,
        models.PaymentMethod.profileType == profileType,
    ).delete()
    db.commit()
    return {"ok": True}
