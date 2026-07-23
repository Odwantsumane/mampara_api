from sqlalchemy.orm import Session

import models
from utils import detect_card_brand


def get_billing_profile(db: Session, profile_type: str) -> models.BillingProfile | None:
    return db.query(models.BillingProfile).filter(models.BillingProfile.profileType == profile_type).first()


def get_payment_methods(db: Session, profile_type: str) -> list[models.PaymentMethod]:
    return db.query(models.PaymentMethod).filter(models.PaymentMethod.profileType == profile_type).all()


def add_payment_method(
    db: Session, profile_type: str, cardholder_name: str, card_number: str, expiry: str, debit_date: str
) -> models.PaymentMethod:
    existing_count = db.query(models.PaymentMethod).filter(models.PaymentMethod.profileType == profile_type).count()
    method = models.PaymentMethod(
        profileType=profile_type,
        type="card",
        brand=detect_card_brand(card_number),
        last4=card_number[-4:],
        cardNumber=card_number,
        cardholderName=cardholder_name,
        expiry=expiry,
        debitDate=debit_date,
        isPrimary=existing_count == 0,
    )
    db.add(method)
    db.commit()
    db.refresh(method)
    return method


def update_payment_method(
    db: Session, method_id: str, profile_type: str, cardholder_name: str, card_number: str, expiry: str, debit_date: str
) -> models.PaymentMethod | None:
    method = db.query(models.PaymentMethod).filter(
        models.PaymentMethod.id == method_id,
        models.PaymentMethod.profileType == profile_type,
    ).first()
    if method is None:
        return None
    method.brand = detect_card_brand(card_number)
    method.last4 = card_number[-4:]
    method.cardNumber = card_number
    method.cardholderName = cardholder_name
    method.expiry = expiry
    method.debitDate = debit_date
    db.commit()
    db.refresh(method)
    return method


def remove_payment_method(db: Session, method_id: str, profile_type: str) -> None:
    db.query(models.PaymentMethod).filter(
        models.PaymentMethod.id == method_id,
        models.PaymentMethod.profileType == profile_type,
    ).delete()
    db.commit()
