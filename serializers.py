"""Shared helpers for turning ORM rows into the plain dicts the frontend expects."""

import models


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
    }


def advance_to_dict(advance: models.Advance) -> dict:
    return {
        "id": advance.id,
        "borrower": advance.borrower,
        "principal": advance.principal,
        "fee": advance.fee,
        "due": advance.due,
        "status": advance.status,
        "statusIcon": advance.statusIcon,
        "statusClass": advance.statusClass,
    }


def kyc_document_to_dict(doc: models.KycDocument) -> dict:
    return {
        "key": doc.key,
        "category": doc.category,
        "fileName": doc.fileName,
        "status": doc.status,
        "type": doc.type,
        "url": doc.url,
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


def invoice_to_dict(invoice: models.Invoice) -> dict:
    return {"id": invoice.id, "date": invoice.date, "amount": invoice.amount}
