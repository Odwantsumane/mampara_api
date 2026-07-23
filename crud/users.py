from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.userAuthentication import verify_password
import models

# Only these fields are ever editable — via the Personal Information form or
# the Notification/Security preference toggles — anything else passed to
# update_user is ignored rather than blindly applied.
EDITABLE_FIELDS = {
    "inputNames", "inputSurnames", "inputIdNumber", "inputPhone", "inputResidency",
    "notifyEmail", "notifyPush", "notifySms", "notifyNewsletter", "loginAlerts",
}


def create_user(db: Session, **fields) -> models.User:
    db_user = models.User(**fields)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).all()


def get_borrowers(db: Session) -> list[models.User]:
    return db.query(models.User).filter(models.User.profileType == "borrower").all()


def get_user_by_id(db: Session, user_id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(func.lower(models.User.email) == email.lower()).first()


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None
    return user


def update_user(db: Session, user_id: str, fields: dict) -> models.User | None:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for key, value in fields.items():
        if key in EDITABLE_FIELDS:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: str, new_hashed_password: str) -> models.User | None:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.password = new_hashed_password
    db.commit()
    return user


def delete_user(db: Session, user_id: str) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
