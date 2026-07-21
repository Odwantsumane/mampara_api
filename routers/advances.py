from fastapi import APIRouter, HTTPException

import store
from schemas import AdvanceDecisionRequest, CreateAdvanceRequest

router = APIRouter(prefix="/api/advances", tags=["advances"])


@router.get("")
def get_advance_book(profileType: str, borrowerName: str = ""):
    if profileType == "borrower" and borrowerName:
        return [row for row in store.advances if row["borrower"] == borrowerName]
    return store.advances


@router.post("")
def create_advance_application(payload: CreateAdvanceRequest):
    fee = round(payload.principal * (payload.feePercent / 100), 2)
    record = {
        "id": store.next_advance_id(),
        "borrower": payload.borrowerName,
        "principal": f"R {payload.principal:,.2f}",
        "fee": f"{payload.feePercent:g}% (R {fee:,.2f})",
        "due": f"Due in {payload.termDays} days",
        "status": "Pending Approval",
        "statusIcon": "bi-hourglass-split",
        "statusClass": "secondary",
    }
    store.advances.insert(0, record)
    return record


def _find_advance(advance_id: str) -> dict:
    row = next((r for r in store.advances if r["id"] == advance_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Advance not found.")
    return row


# advance ids look like "#ADV-2026-892" — the "#" makes them unsafe as a raw
# URL path segment (browsers treat it as a fragment delimiter), so the id is
# passed in the request body instead of the path.
@router.post("/approve")
def approve_advance(payload: AdvanceDecisionRequest):
    row = _find_advance(payload.id)
    row.update({"status": "Performing", "statusIcon": "bi-check-circle-fill", "statusClass": "success"})
    return row


@router.post("/decline")
def decline_advance(payload: AdvanceDecisionRequest):
    row = _find_advance(payload.id)
    row.update({"status": "Declined", "statusIcon": "bi-x-circle-fill", "statusClass": "danger"})
    return row
