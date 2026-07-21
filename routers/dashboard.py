from fastapi import APIRouter, HTTPException

import store

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(profileType: str, firstName: str = ""):
    if profileType not in store.dashboard_copy:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    copy = dict(store.dashboard_copy[profileType])
    copy["dashboardSubtitle"] = copy["dashboardSubtitle"].replace("{name}", firstName or "there")
    return {
        "copy": copy,
        "trendChart": store.trend_chart_data,
        "allocationChart": store.allocation_chart_data,
    }


@router.get("/public-teaser")
def get_public_teaser():
    return store.public_teaser
