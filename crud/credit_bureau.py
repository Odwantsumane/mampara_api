import requests
from sqlalchemy.orm import Session

import constants
import models


def find_borrower_by_id_number(db: Session, id_number: str) -> models.User | None:
    if not id_number:
        return None
    return db.query(models.User).filter(models.User.inputIdNumber == id_number).first()


def run_bureau_lookup(name: str, id_number: str, bureau: str) -> dict:
    """Calls out to the configured credit bureau (constants.CREDIT_BUREAU_API_URL)
    and returns its raw JSON response. Raises requests.RequestException on
    network failure or a non-2xx status — callers decide how to surface that."""
    response = requests.post(
        constants.CREDIT_BUREAU_API_URL,
        json={"name": name, "idNumber": id_number, "bureau": bureau},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def save_credit_score(
    db: Session, *, borrower_id: str | None, name: str, id_number: str, bureau: str, result: dict
) -> models.CreditScoreRecord:
    record = models.CreditScoreRecord(
        borrowerId=borrower_id,
        name=name,
        idNumber=id_number,
        bureau=bureau,
        score=result["score"],
        scoreScaleLabel=result["scoreScaleLabel"],
        riskLabel=result["riskLabel"],
        defaultJudgements=result["defaultJudgements"],
        openFacilities=result["openFacilities"],
        affordability=result["affordability"],
        recommendedMaxAdvance=result["recommendedMaxAdvance"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_credit_score(db: Session, borrower_id: str) -> models.CreditScoreRecord | None:
    return (
        db.query(models.CreditScoreRecord)
        .filter(models.CreditScoreRecord.borrowerId == borrower_id)
        .order_by(models.CreditScoreRecord.created_at.desc())
        .first()
    )
