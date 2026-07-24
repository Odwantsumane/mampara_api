import uuid

import requests
from sqlalchemy.orm import Session

import constants
import models


def new_reference() -> str:
    return f"pay_{uuid.uuid4().hex[:16]}"


def initialize_transaction(email: str, amount_rand: float, reference: str, callback_url: str) -> dict:
    """Real outbound call to the configured gateway (constants.PAYSTACK_BASE_URL)
    — mirrors Paystack's actual /transaction/initialize request/response shape
    so swapping in a real Paystack account later is a config-only change."""
    response = requests.post(
        f"{constants.PAYSTACK_BASE_URL}/transaction/initialize",
        json={
            "email": email,
            "amount": round(amount_rand * 100),  # smallest currency unit, as Paystack expects
            "reference": reference,
            "callback_url": callback_url,
        },
        headers={"Authorization": f"Bearer {constants.PAYSTACK_SECRET_KEY}"},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def verify_transaction(reference: str) -> dict:
    response = requests.get(
        f"{constants.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {constants.PAYSTACK_SECRET_KEY}"},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def create_payment(
    db: Session, *, reference: str, advance_id: str, borrower_id: str, amount: float, authorization_url: str
) -> models.Payment:
    payment = models.Payment(
        reference=reference,
        advanceId=advance_id,
        borrowerId=borrower_id,
        amount=amount,
        status="Pending",
        authorizationUrl=authorization_url,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_reference(db: Session, reference: str) -> models.Payment | None:
    return db.query(models.Payment).filter(models.Payment.reference == reference).first()


def mark_payment_status(db: Session, reference: str, status: str) -> models.Payment | None:
    payment = get_payment_by_reference(db, reference)
    if not payment:
        return None
    payment.status = status
    db.commit()
    db.refresh(payment)
    return payment


def get_all_payments(db: Session) -> list[models.Payment]:
    return db.query(models.Payment).order_by(models.Payment.created_at.desc()).all()
