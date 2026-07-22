from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas import UploadKycDocumentRequest
from serializers import kyc_document_to_dict
from utils import next_kyc_key

router = APIRouter(prefix="/api/kyc", tags=["kyc"])


@router.get("/queue")
def get_kyc_queue(db: Session = Depends(get_db)):
    rows = db.query(models.KycDocument).all()
    return [kyc_document_to_dict(row) for row in rows]


@router.post("/documents")
def upload_kyc_document(payload: UploadKycDocumentRequest, db: Session = Depends(get_db)):
    doc = models.KycDocument(
        key=next_kyc_key(),
        category=payload.category,
        fileName=payload.fileName,
        status="Pending Review",
        type=payload.type,
        url=payload.url,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return kyc_document_to_dict(doc)


@router.delete("/documents/{key}")
def remove_kyc_document(key: str, db: Session = Depends(get_db)):
    db.query(models.KycDocument).filter(models.KycDocument.key == key).delete()
    db.commit()
    return {"ok": True}
