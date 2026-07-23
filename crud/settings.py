from sqlalchemy.orm import Session

import models


def get_settings(db: Session) -> models.PlatformSettings:
    return db.query(models.PlatformSettings).filter(models.PlatformSettings.id == 1).first()


def update_settings(
    db: Session, advance_fee_percent: float | None = None, universal_advance_limit: float | None = None
) -> models.PlatformSettings:
    row = get_settings(db)
    if advance_fee_percent is not None:
        row.advanceFeePercent = advance_fee_percent
    if universal_advance_limit is not None:
        row.universalAdvanceLimit = universal_advance_limit
    db.commit()
    return row
