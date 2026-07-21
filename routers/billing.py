from fastapi import APIRouter, HTTPException

import store
from schemas import AddPaymentMethodRequest, UpdatePaymentMethodRequest

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("")
def get_billing(profileType: str):
    if profileType not in store.billing:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    return store.billing[profileType]


@router.post("/payment-methods")
def add_payment_method(payload: AddPaymentMethodRequest):
    profile = store.billing.get(payload.profileType)
    if profile is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    method = {
        "id": store.next_payment_method_id(),
        "type": "card",
        "brand": store.detect_card_brand(payload.cardNumber),
        "last4": payload.cardNumber[-4:],
        "cardNumber": payload.cardNumber,
        "cardholderName": payload.cardholderName,
        "expiry": payload.expiry,
        "debitDate": payload.debitDate,
        "isPrimary": len(profile.get("paymentMethods", [])) == 0,
    }
    profile.setdefault("paymentMethods", []).append(method)
    return method


@router.patch("/payment-methods/{method_id}")
def update_payment_method(method_id: str, payload: UpdatePaymentMethodRequest):
    profile = store.billing.get(payload.profileType)
    if profile is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    methods = profile.get("paymentMethods", [])
    method = next((m for m in methods if m["id"] == method_id), None)
    if method is None:
        raise HTTPException(status_code=404, detail="Payment method not found.")
    method.update({
        "brand": store.detect_card_brand(payload.cardNumber),
        "last4": payload.cardNumber[-4:],
        "cardNumber": payload.cardNumber,
        "cardholderName": payload.cardholderName,
        "expiry": payload.expiry,
        "debitDate": payload.debitDate,
    })
    return method


@router.delete("/payment-methods/{method_id}")
def remove_payment_method(method_id: str, profileType: str):
    profile = store.billing.get(profileType)
    if profile is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    profile["paymentMethods"] = [m for m in profile.get("paymentMethods", []) if m["id"] != method_id]
    return {"ok": True}
