from fastapi import APIRouter

import store
from schemas import CreditCheckRequest

router = APIRouter(prefix="/api/credit-bureau", tags=["credit-bureau"])


@router.post("/check")
def run_credit_check(payload: CreditCheckRequest):
    return {
        **store.credit_bureau_result,
        "name": payload.name or store.credit_bureau_result["name"],
        "idNumber": payload.idNumber or store.credit_bureau_result["idNumber"],
        "bureau": payload.bureau,
    }
