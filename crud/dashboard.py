from sqlalchemy.orm import Session

import models
from crud.advances import get_advance_book

# Statuses where "repayment due on <date>" is still a meaningful, forward-looking
# thing to show — excludes terminal states (Declined/Defaulted).
ACTIVE_ADVANCE_STATUSES = {"Performing", "Late", "Pending Approval"}


def get_dashboard_copy(db: Session, profile_type: str) -> models.DashboardCopy | None:
    return db.query(models.DashboardCopy).filter(models.DashboardCopy.profileType == profile_type).first()


def get_borrower_active_advance(db: Session, borrower_id: str) -> models.Advance | None:
    """The borrower's soonest-due active advance, if any — used to make the
    dashboard's "Active Advance Balance" card reflect real data instead of a
    frozen mock balance/date."""
    active = [a for a in get_advance_book(db, "borrower", borrower_id) if a.status in ACTIVE_ADVANCE_STATUSES]
    if not active:
        return None
    return min(active, key=lambda a: a.dueDate)


def get_public_teaser(db: Session) -> models.PublicTeaser:
    return db.query(models.PublicTeaser).filter(models.PublicTeaser.id == 1).first()
