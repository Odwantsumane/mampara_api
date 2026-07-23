"""
Populates a freshly-created (empty) database with the dummy content from
seed_data.py. Safe to call every startup — it only inserts rows for tables
that are still empty, so real data entered later is never overwritten.
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

import models
import seed_data
from auth.userAuthentication import hash_password


def seed_if_empty(db: Session) -> None:
    if db.query(models.User).count() == 0:
        for user in seed_data.users:
            db.add(models.User(**{**user, "password": hash_password(user["password"])}))
        # flush immediately: kyc_documents.userId is a FK to users.id, and
        # without a relationship() between the two mappers the flush doesn't
        # reliably order cross-table inserts by dependency (it sorted
        # "kyc_documents" before "users" here), so force it explicitly.
        db.flush()

    if db.query(models.Advance).count() == 0:
        for order, advance in enumerate(seed_data.advances):
            fields = {k: v for k, v in advance.items() if k != "dueInDays"}
            due_date = date.today() + timedelta(days=advance["dueInDays"])
            db.add(models.Advance(**fields, dueDate=due_date, sortOrder=order))

    if db.query(models.KycDocument).count() == 0:
        for doc in seed_data.kyc_queue:
            db.add(models.KycDocument(**doc))

    if db.query(models.BillingProfile).count() == 0:
        for profile_type, profile in seed_data.billing.items():
            db.add(models.BillingProfile(profileType=profile_type))
            for method in profile["paymentMethods"]:
                db.add(models.PaymentMethod(profileType=profile_type, **method))

    if db.query(models.PlatformSettings).count() == 0:
        db.add(models.PlatformSettings(id=1, **seed_data.default_settings))

    if db.query(models.DashboardCopy).count() == 0:
        for profile_type, copy in seed_data.dashboard_copy.items():
            db.add(models.DashboardCopy(profileType=profile_type, copy=copy))

    if db.query(models.ChartData).count() == 0:
        db.add(models.ChartData(id="trend", data=seed_data.trend_chart_data))
        db.add(models.ChartData(id="allocation", data=seed_data.allocation_chart_data))

    if db.query(models.PublicTeaser).count() == 0:
        db.add(models.PublicTeaser(id=1, data=seed_data.public_teaser))

    db.commit()
