"""
Populates a freshly-created (empty) database with the dummy content from
seed_data.py. Safe to call every startup — it only inserts rows for tables
that are still empty, so real data entered later is never overwritten.
"""

from sqlalchemy.orm import Session

import models
import seed_data


def seed_if_empty(db: Session) -> None:
    if db.query(models.User).count() == 0:
        for user in seed_data.users:
            db.add(models.User(**user))

    if db.query(models.Advance).count() == 0:
        for order, advance in enumerate(seed_data.advances):
            db.add(models.Advance(**advance, sortOrder=order))

    if db.query(models.KycDocument).count() == 0:
        for doc in seed_data.kyc_queue:
            db.add(models.KycDocument(**doc))

    if db.query(models.BillingProfile).count() == 0:
        for profile_type, profile in seed_data.billing.items():
            db.add(models.BillingProfile(
                profileType=profile_type,
                planName=profile["planName"],
                planPrice=profile["planPrice"],
                renewsOn=profile["renewsOn"],
            ))
            for method in profile["paymentMethods"]:
                db.add(models.PaymentMethod(profileType=profile_type, **method))
            for invoice in profile["invoices"]:
                db.add(models.Invoice(profileType=profile_type, **invoice))

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

    if db.query(models.CreditBureauTemplate).count() == 0:
        db.add(models.CreditBureauTemplate(id=1, data=seed_data.credit_bureau_result))

    db.commit()
