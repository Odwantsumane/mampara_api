from fastapi import APIRouter

import store
from schemas import UploadKycDocumentRequest

router = APIRouter(prefix="/api/kyc", tags=["kyc"])


@router.get("/queue")
def get_kyc_queue():
    return store.kyc_queue


@router.post("/documents")
def upload_kyc_document(payload: UploadKycDocumentRequest):
    record = {
        "key": store.next_kyc_key(),
        "category": payload.category,
        "fileName": payload.fileName,
        "status": "Pending Review",
        "type": payload.type,
        "url": payload.url,
    }
    store.kyc_queue.append(record)
    return record


@router.delete("/documents/{key}")
def remove_kyc_document(key: str):
    store.kyc_queue[:] = [row for row in store.kyc_queue if row["key"] != key]
    return {"ok": True}
