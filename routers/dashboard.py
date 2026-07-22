from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(profileType: str, firstName: str = "", db: Session = Depends(get_db)):
    row = db.query(models.DashboardCopy).filter(models.DashboardCopy.profileType == profileType).first()
    if row is None:
        raise HTTPException(status_code=400, detail="Unknown profile type.")
    copy = {**row.copy}
    copy["dashboardSubtitle"] = copy["dashboardSubtitle"].replace("{name}", firstName or "there")

    trend = db.query(models.ChartData).filter(models.ChartData.id == "trend").first()
    allocation = db.query(models.ChartData).filter(models.ChartData.id == "allocation").first()

    return {
        "copy": copy,
        "trendChart": trend.data,
        "allocationChart": allocation.data,
    }


@router.get("/public-teaser")
def get_public_teaser(db: Session = Depends(get_db)):
    row = db.query(models.PublicTeaser).filter(models.PublicTeaser.id == 1).first()
    return row.data
