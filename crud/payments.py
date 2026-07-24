import uuid

from sqlalchemy.orm import Session

import models


def new_reference() -> str:
    return f"pay_{uuid.uuid4().hex[:16]}"


def create_pending_payment(db: Session, *, reference: str, advance_id: str, borrower_id: str, amount: float) -> models.Payment:
    payment = models.Payment(
        reference=reference,
        advanceId=advance_id,
        borrowerId=borrower_id,
        amount=amount,
        status="Pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_id(db: Session, payment_id: str) -> models.Payment | None:
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()


def get_payment_by_reference(db: Session, reference: str) -> models.Payment | None:
    return db.query(models.Payment).filter(models.Payment.reference == reference).first()


def confirm_payment(db: Session, payment_id: str) -> models.Payment | None:
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return None
    payment.status = "Confirmed"
    db.commit()
    db.refresh(payment)
    return payment


def cancel_payment(db: Session, payment_id: str) -> models.Payment | None:
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return None
    payment.status = "Cancelled"
    db.commit()
    db.refresh(payment)
    return payment


def get_all_payments(db: Session) -> list[models.Payment]:
    return db.query(models.Payment).order_by(models.Payment.created_at.desc()).all()
