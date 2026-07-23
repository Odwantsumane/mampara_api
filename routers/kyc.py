from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

import crud.kyc as kyc_crud
import crud.users as users_crud
from db import get_db
from serializers import kyc_document_to_dict

router = APIRouter(prefix="/api/kyc", tags=["kyc"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.get("/queue")
def get_kyc_queue(borrowerId: str = "", db: Session = Depends(get_db)):
    rows = kyc_crud.get_kyc_queue(db, borrowerId)
    return [kyc_document_to_dict(doc, borrower_name=name) for doc, name in rows]


@router.post("/documents")
async def upload_kyc_document(
    borrowerId: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit.")
    doc = await kyc_crud.create_kyc_document(db, borrowerId, category, file)
    borrower = users_crud.get_user_by_id(db, borrowerId)
    return kyc_document_to_dict(doc, borrower_name=borrower.name if borrower else None)


@router.delete("/documents/{key}")
def remove_kyc_document(key: str, db: Session = Depends(get_db)):
    kyc_crud.delete_kyc_document(db, key)
    return {"ok": True}


@router.post("/documents/{key}/approve")
def approve_kyc_document(key: str, db: Session = Depends(get_db)):
    doc = kyc_crud.set_status(db, key, "Approved")
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return kyc_document_to_dict(doc)


@router.post("/documents/{key}/reject")
def reject_kyc_document(key: str, db: Session = Depends(get_db)):
    doc = kyc_crud.set_status(db, key, "Rejected")
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return kyc_document_to_dict(doc)
