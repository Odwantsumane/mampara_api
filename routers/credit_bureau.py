from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas import CreditCheckRequest

router = APIRouter(prefix="/api/credit-bureau", tags=["credit-bureau"])


@router.post("/check")
def run_credit_check(payload: CreditCheckRequest, db: Session = Depends(get_db)):
    template = db.query(models.CreditBureauTemplate).filter(models.CreditBureauTemplate.id == 1).first()
    result = {**template.data}
    return {
        **result,
        "name": payload.name or result["name"],
        "idNumber": payload.idNumber or result["idNumber"],
        "bureau": payload.bureau,
    }
