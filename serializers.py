"""Shared helpers for turning ORM rows into the plain dicts the frontend expects."""

import models
from utils import format_due_text


def user_to_dict(user: models.User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "profileType": user.profileType,
        "name": user.name,
        "role": user.role,
        "badgeIcon": user.badgeIcon,
        "badgeText": user.badgeText,
        "tier": user.tier,
        "avatar": user.avatar,
        "inputNames": user.inputNames,
        "inputSurnames": user.inputSurnames,
        "inputIdNumber": user.inputIdNumber,
        "inputPhone": user.inputPhone,
        "inputResidency": user.inputResidency,
        "notifyEmail": user.notifyEmail,
        "notifyPush": user.notifyPush,
        "notifySms": user.notifySms,
        "notifyNewsletter": user.notifyNewsletter,
        "loginAlerts": user.loginAlerts,
    }


def advance_to_dict(advance: models.Advance) -> dict:
    return {
        "id": advance.id,
        "borrower": advance.borrower,
        "principal": advance.principal,
        "fee": advance.fee,
        "due": format_due_text(advance.dueDate),
        "status": advance.status,
        "statusIcon": advance.statusIcon,
        "statusClass": advance.statusClass,
    }


def kyc_document_to_dict(doc: models.KycDocument, borrower_name: str | None = None) -> dict:
    url = doc.filePath if doc.filePath.startswith("http") else f"/uploads/{doc.filePath}"
    return {
        "key": doc.key,
        "borrowerId": doc.userId,
        "borrowerName": borrower_name,
        "category": doc.category,
        "categoryLabel": doc.categoryLabel,
        "fileName": doc.fileName,
        "status": doc.status,
        "type": doc.type,
        "url": url,
    }


def credit_score_to_dict(record: models.CreditScoreRecord) -> dict:
    return {
        "id": record.id,
        "borrowerId": record.borrowerId,
        "name": record.name,
        "idNumber": record.idNumber,
        "bureau": record.bureau,
        "score": record.score,
        "scoreScaleLabel": record.scoreScaleLabel,
        "riskLabel": record.riskLabel,
        "defaultJudgements": record.defaultJudgements,
        "openFacilities": record.openFacilities,
        "affordability": record.affordability,
        "recommendedMaxAdvance": record.recommendedMaxAdvance,
        "checkedAt": record.created_at.isoformat() if record.created_at else None,
    }


def payment_to_dict(payment: models.Payment, borrower_name: str | None = None) -> dict:
    return {
        "id": payment.id,
        "reference": payment.reference,
        "advanceId": payment.advanceId,
        "borrowerId": payment.borrowerId,
        "borrowerName": borrower_name,
        "amount": payment.amount,
        "status": payment.status,
        "createdAt": payment.created_at.isoformat() if payment.created_at else None,
    }


def payment_method_to_dict(method: models.PaymentMethod) -> dict:
    return {
        "id": method.id,
        "type": method.type,
        "brand": method.brand,
        "last4": method.last4,
        "cardNumber": method.cardNumber,
        "cardholderName": method.cardholderName,
        "expiry": method.expiry,
        "debitDate": method.debitDate,
        "label": method.label,
        "isPrimary": method.isPrimary,
    }
