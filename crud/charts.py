"""Real, computed chart series — no fabricated numbers. A period with no
activity sums to a genuine 0 rather than a fake placeholder; a category
that has never occurred is omitted rather than padded in with a fake zero
slice."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

import models
from utils import parse_currency

# Ever actually disbursed to the borrower — Pending Approval and Declined
# never resulted in money moving, so they're excluded from disbursement volume.
EVER_DISBURSED_STATUSES = {"Performing", "Late", "Defaulted", "Repaid"}

# Fixed display order for the status-breakdown chart, so colors stay
# consistent across reloads regardless of which statuses are present.
STATUS_ORDER = ["Performing", "Late", "Pending Approval", "Repaid", "Defaulted", "Declined"]


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _weekly_series(rows: list[tuple[date, float]], weeks: int) -> dict:
    today = date.today()
    current_week_start = _week_start(today)
    week_starts = [current_week_start - timedelta(weeks=i) for i in range(weeks - 1, -1, -1)]
    buckets = {ws: 0.0 for ws in week_starts}
    for event_date, amount in rows:
        ws = _week_start(event_date)
        if ws in buckets:
            buckets[ws] += amount
    labels = [f"{ws.strftime('%b')} {ws.day}" for ws in week_starts]
    values = [round(buckets[ws], 2) for ws in week_starts]
    return {"labels": labels, "values": values}


def get_disbursement_trend(db: Session, borrower_id: str = "", weeks: int = 8) -> dict:
    """Weekly disbursement volume for the last `weeks` calendar weeks —
    borrower_id="" aggregates the whole platform (admin view)."""
    query = db.query(models.Advance).filter(models.Advance.status.in_(EVER_DISBURSED_STATUSES))
    if borrower_id:
        query = query.filter(models.Advance.borrowerId == borrower_id)
    rows = [(a.created_at.date(), parse_currency(a.principal)) for a in query.all()]
    series = _weekly_series(rows, weeks)
    return {**series, "label": "Weekly Disbursement Volume (R)"}


def get_repayment_trend(db: Session, borrower_id: str = "", weeks: int = 8) -> dict:
    """Weekly successful-repayment volume — real Paystack (or mock) payment
    confirmations, not advance status changes."""
    query = db.query(models.Payment).filter(models.Payment.status == "Success")
    if borrower_id:
        query = query.filter(models.Payment.borrowerId == borrower_id)
    rows = [(p.created_at.date(), p.amount) for p in query.all()]
    series = _weekly_series(rows, weeks)
    return {**series, "label": "Weekly Repayments (R)"}


def get_status_breakdown(db: Session, borrower_id: str = "") -> dict:
    """Advance-book composition by status, in rand value. borrower_id=""
    aggregates the whole platform (admin view)."""
    query = db.query(models.Advance)
    if borrower_id:
        query = query.filter(models.Advance.borrowerId == borrower_id)
    totals: dict[str, float] = {}
    for advance in query.all():
        totals[advance.status] = totals.get(advance.status, 0.0) + parse_currency(advance.principal)
    labels = [status for status in STATUS_ORDER if status in totals]
    values = [round(totals[status], 2) for status in labels]
    return {"labels": labels, "values": values}
