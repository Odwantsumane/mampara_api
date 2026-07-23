import time
from datetime import date, timedelta

from sqlalchemy.orm import Session

import models
from utils import next_advance_id, parse_currency

# Currently disbursed and still being repaid.
ACTIVE_STATUSES = {"Performing", "Late"}
# Ever actually disbursed — the denominator for a default rate. Pending
# Approval and Declined were never funded, so they can't "default".
DISBURSED_STATUSES = {"Performing", "Late", "Defaulted"}
# Counts against a borrower's advance limit — everything except Declined
# (rejected, never became a real commitment).
COMMITTED_STATUSES = {"Performing", "Late", "Defaulted", "Pending Approval"}


def get_advance_book(db: Session, profile_type: str, borrower_id: str = "") -> list[models.Advance]:
    query = db.query(models.Advance)
    if profile_type == "borrower" and borrower_id:
        query = query.filter(models.Advance.borrowerId == borrower_id)
    return query.order_by(models.Advance.sortOrder.asc()).all()


def get_portfolio_summary(db: Session) -> dict:
    """Aggregates the admin dashboard's headline KPIs straight from the
    advances table instead of frozen mock numbers."""
    rows = db.query(models.Advance).all()

    active_total = sum(parse_currency(r.principal) for r in rows if r.status in ACTIVE_STATUSES)

    pending_rows = [r for r in rows if r.status == "Pending Approval"]
    pending_total = sum(parse_currency(r.principal) for r in pending_rows)

    disbursed_rows = [r for r in rows if r.status in DISBURSED_STATUSES]
    defaulted_count = sum(1 for r in disbursed_rows if r.status == "Defaulted")
    default_rate_percent = (defaulted_count / len(disbursed_rows) * 100) if disbursed_rows else 0.0

    return {
        "activeTotal": active_total,
        "pendingTotal": pending_total,
        "pendingCount": len(pending_rows),
        "defaultRatePercent": default_rate_percent,
    }


def get_active_advance_count(db: Session, borrower_id: str) -> int:
    return (
        db.query(models.Advance)
        .filter(models.Advance.borrowerId == borrower_id, models.Advance.status.in_(ACTIVE_STATUSES))
        .count()
    )


def get_borrower_committed_total(db: Session, borrower_id: str) -> float:
    """Sum of principal the borrower has already committed against their
    limit — active balances, defaults still owed, and pending requests
    (reserved so they can't stack multiple simultaneous applications past
    their limit). Declined applications never happened, so they're excluded."""
    rows = db.query(models.Advance).filter(models.Advance.borrowerId == borrower_id).all()
    return sum(parse_currency(r.principal) for r in rows if r.status in COMMITTED_STATUSES)


def record_daily_snapshot(db: Session, summary: dict) -> None:
    """Upserts today's row in portfolio_snapshots. Called every time the
    admin dashboard loads, so today's snapshot always reflects the latest
    known numbers — real history accumulates automatically, one day at a
    time, with no separate scheduler needed."""
    today = date.today()
    existing = db.query(models.PortfolioSnapshot).filter(models.PortfolioSnapshot.snapshotDate == today).first()
    if existing:
        existing.activeTotal = summary["activeTotal"]
        existing.pendingTotal = summary["pendingTotal"]
        existing.defaultRatePercent = summary["defaultRatePercent"]
    else:
        db.add(models.PortfolioSnapshot(
            snapshotDate=today,
            activeTotal=summary["activeTotal"],
            pendingTotal=summary["pendingTotal"],
            defaultRatePercent=summary["defaultRatePercent"],
        ))
    db.commit()


def get_baseline_snapshot(db: Session, on_or_before: date) -> models.PortfolioSnapshot | None:
    """The most recent snapshot dated on_or_before — i.e. "at least this old".
    Returns None if we don't have data going back that far yet."""
    return (
        db.query(models.PortfolioSnapshot)
        .filter(models.PortfolioSnapshot.snapshotDate <= on_or_before)
        .order_by(models.PortfolioSnapshot.snapshotDate.desc())
        .first()
    )


def create_advance(db: Session, borrower: models.User, principal: float, fee_percent: float, term_days: int) -> models.Advance:
    fee = round(principal * (fee_percent / 100), 2)
    advance = models.Advance(
        id=next_advance_id(),
        borrowerId=borrower.id,
        # the display name is resolved from the real user record here, not
        # trusted from client input, so an advance can never reference a
        # name that doesn't match its own borrowerId
        borrower=borrower.name,
        principal=f"R {principal:,.2f}",
        fee=f"{fee_percent:g}% (R {fee:,.2f})",
        dueDate=date.today() + timedelta(days=term_days),
        status="Pending Approval",
        statusIcon="bi-hourglass-split",
        statusClass="secondary",
        # newer advances sort first, matching the old in-memory mock's list.insert(0, ...)
        sortOrder=-int(time.time() * 1000),
    )
    db.add(advance)
    db.commit()
    db.refresh(advance)
    return advance


def get_advance_by_id(db: Session, advance_id: str) -> models.Advance | None:
    return db.query(models.Advance).filter(models.Advance.id == advance_id).first()


def approve_advance(db: Session, advance_id: str) -> models.Advance | None:
    advance = get_advance_by_id(db, advance_id)
    if not advance:
        return None
    advance.status = "Performing"
    advance.statusIcon = "bi-check-circle-fill"
    advance.statusClass = "success"
    db.commit()
    db.refresh(advance)
    return advance


def decline_advance(db: Session, advance_id: str) -> models.Advance | None:
    advance = get_advance_by_id(db, advance_id)
    if not advance:
        return None
    advance.status = "Declined"
    advance.statusIcon = "bi-x-circle-fill"
    advance.statusClass = "danger"
    db.commit()
    db.refresh(advance)
    return advance
