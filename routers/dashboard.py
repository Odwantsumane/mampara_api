from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud.advances as advances_crud
import crud.charts as charts_crud
import crud.dashboard as dashboard_crud
import crud.kyc as kyc_crud
import crud.settings as settings_crud
from db import get_db
from utils import format_calendar_date, format_rand_whole, percent_change

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

TREND_WINDOW_DAYS = 30


def _clear_trend(copy: dict, prefix: str) -> None:
    """No fake trend when we don't have history old enough to compare
    against yet — no icon, no invented percentage, just a plain note. Once
    30 days of real snapshots exist this stops firing on its own."""
    copy[f"{prefix}SubIcon"] = None
    copy[f"{prefix}SubText"] = "Not enough history yet"
    copy[f"{prefix}SubClass"] = "text-muted"


@router.get("")
def get_dashboard(
    profileType: str, firstName: str = "", borrowerId: str = "", db: Session = Depends(get_db)
):
    row = dashboard_crud.get_dashboard_copy(db, profileType)
    if row is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    copy = {**row.copy}
    copy["dashboardSubtitle"] = copy["dashboardSubtitle"].replace("{name}", firstName or "there")

    available_limit = None
    kyc_status = None
    trend = {"labels": [], "values": [], "label": ""}
    allocation = {"labels": [], "values": []}

    if profileType == "admin":
        summary = advances_crud.get_portfolio_summary(db)
        advances_crud.record_daily_snapshot(db, summary)
        trend = charts_crud.get_disbursement_trend(db)
        allocation = charts_crud.get_status_breakdown(db)

        copy["card1Value"] = format_rand_whole(summary["activeTotal"])
        copy["card2Value"] = format_rand_whole(summary["pendingTotal"])
        pending_count = summary["pendingCount"]
        copy["card2Sub"] = f"{pending_count} application{'s' if pending_count != 1 else ''} awaiting sign-off"
        copy["card3Value"] = f"{summary['defaultRatePercent']:.1f}%"

        baseline = advances_crud.get_baseline_snapshot(db, date.today() - timedelta(days=TREND_WINDOW_DAYS))
        if baseline:
            active_delta = percent_change(baseline.activeTotal, summary["activeTotal"])
            if active_delta is not None:
                copy["card1SubIcon"] = "bi-arrow-up-right" if active_delta >= 0 else "bi-arrow-down-right"
                copy["card1SubText"] = f"{active_delta:+.1f}% from last month"
                copy["card1SubClass"] = "text-success" if active_delta >= 0 else "text-danger"
            else:
                _clear_trend(copy, "card1")

            default_delta = summary["defaultRatePercent"] - baseline.defaultRatePercent
            copy["card3SubIcon"] = "bi-arrow-up-right" if default_delta >= 0 else "bi-arrow-down-right"
            copy["card3SubText"] = f"{default_delta:+.1f} pts vs last month"
            copy["card3SubClass"] = "text-danger" if default_delta > 0 else "text-success"
        else:
            _clear_trend(copy, "card1")
            _clear_trend(copy, "card3")
    elif profileType == "borrower" and borrowerId:
        active_advance = dashboard_crud.get_borrower_active_advance(db, borrowerId)
        if active_advance:
            copy["card1Value"] = active_advance.principal
            copy["card1SubText"] = f"Repayment due {format_calendar_date(active_advance.dueDate)} (payday)"
        else:
            copy["card1Value"] = "R 0"
            copy["card1SubText"] = "No active advance — apply from the calculator below"

        settings_row = settings_crud.get_settings(db)
        limit_info = advances_crud.get_borrower_limit_info(db, borrowerId, settings_row.universalAdvanceLimit)
        available_limit = limit_info["availableLimit"]
        tier_limit = limit_info["tierLimit"]
        copy["card2Value"] = format_rand_whole(available_limit)
        if limit_info["committedTotal"] > 0:
            copy["card2Sub"] = (
                f"{format_rand_whole(tier_limit)} limit "
                f"— {format_rand_whole(limit_info['committedTotal'])} already borrowed"
            )
        elif limit_info["nextTier"]:
            next_threshold, next_percentage = limit_info["nextTier"]
            remaining = next_threshold - limit_info["repaidCount"]
            next_limit = settings_row.universalAdvanceLimit * next_percentage
            copy["card2Sub"] = (
                f"{format_rand_whole(tier_limit)} limit — repay {remaining} more advance"
                f"{'s' if remaining != 1 else ''} to reach {format_rand_whole(next_limit)}"
            )
        else:
            copy["card2Sub"] = f"{format_rand_whole(tier_limit)} limit — maximum tier reached"

        kyc_status = kyc_crud.get_kyc_completeness(db, borrowerId)
        trend = charts_crud.get_repayment_trend(db, borrowerId)
        allocation = charts_crud.get_status_breakdown(db, borrowerId)

    return {
        "copy": copy,
        "trendChart": trend,
        "allocationChart": allocation,
        "availableLimit": available_limit,
        "kycStatus": kyc_status,
    }


@router.get("/public-teaser")
def get_public_teaser(db: Session = Depends(get_db)):
    teaser = dashboard_crud.get_public_teaser(db).data
    allocation = charts_crud.get_status_breakdown(db)
    return {**teaser, "allocationLabels": allocation["labels"], "allocationValues": allocation["values"]}
