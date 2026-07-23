import pathlib
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

import models

UPLOAD_ROOT = pathlib.Path("uploads") / "approval"

KYC_DOCUMENT_TYPES = {
    "id_document": "South African Green ID Book or Smart ID Card",
    "proof_of_residence": "Proof of Residence (Utility Bill < 3 months)",
    "payslip": "Latest 3 Months Bank Statements / Payslip",
    "tax_certificate": "SARS Tax Clearance / Notice of Assessment",
}


def get_kyc_queue(db: Session, borrower_id: str = "") -> list[tuple[models.KycDocument, str]]:
    """(document, borrowerName) pairs. Empty borrower_id returns every
    borrower's documents — used by the admin Risk & Compliance review;
    a specific id scopes it to that borrower's own KYC modal."""
    query = db.query(models.KycDocument, models.User.name).join(models.User, models.User.id == models.KycDocument.userId)
    if borrower_id:
        query = query.filter(models.KycDocument.userId == borrower_id)
    return query.order_by(models.KycDocument.created_at.desc()).all()


def _save_upload_bytes(borrower_id: str, filename: str, contents: bytes) -> str:
    suffix = pathlib.Path(filename or "").suffix
    stored_name = f"{uuid.uuid4()}{suffix}"
    dest_dir = UPLOAD_ROOT / borrower_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / stored_name).write_bytes(contents)
    return f"approval/{borrower_id}/{stored_name}"


async def create_kyc_document(db: Session, borrower_id: str, category: str, upload: UploadFile) -> models.KycDocument:
    label = KYC_DOCUMENT_TYPES.get(category, category)
    contents = await upload.read()
    file_path = _save_upload_bytes(borrower_id, upload.filename, contents)
    content_type = upload.content_type or ""
    is_pdf = "pdf" in content_type or (upload.filename or "").lower().endswith(".pdf")
    doc = models.KycDocument(
        userId=borrower_id,
        category=category,
        categoryLabel=label,
        fileName=upload.filename or "document",
        filePath=file_path,
        type="pdf" if is_pdf else "image",
        status="Pending Review",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_kyc_document(db: Session, key: str) -> None:
    db.query(models.KycDocument).filter(models.KycDocument.key == key).delete()
    db.commit()


def set_status(db: Session, key: str, status: str) -> models.KycDocument | None:
    doc = db.query(models.KycDocument).filter(models.KycDocument.key == key).first()
    if not doc:
        return None
    doc.status = status
    db.commit()
    db.refresh(doc)
    return doc


def get_kyc_completeness(db: Session, borrower_id: str) -> dict:
    """Which of the required document categories are missing, still pending
    review, or were rejected — re-uploads after a rejection are handled by
    only looking at each category's most recently uploaded document."""
    docs = db.query(models.KycDocument).filter(models.KycDocument.userId == borrower_id).all()
    latest_by_category: dict[str, models.KycDocument] = {}
    for doc in docs:
        existing = latest_by_category.get(doc.category)
        if not existing or doc.created_at > existing.created_at:
            latest_by_category[doc.category] = doc

    missing, pending, rejected = [], [], []
    for category, label in KYC_DOCUMENT_TYPES.items():
        doc = latest_by_category.get(category)
        if not doc:
            missing.append(label)
        elif doc.status == "Rejected":
            rejected.append(label)
        elif doc.status != "Approved":
            pending.append(label)

    return {
        "complete": not missing and not pending and not rejected,
        "missingCategories": missing,
        "pendingCategories": pending,
        "rejectedCategories": rejected,
    }
