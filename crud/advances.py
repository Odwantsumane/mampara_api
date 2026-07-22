from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, case, func
from models import Advance
from schemas import CreateAdvanceRequest

def create_notification(db: Session, notification: CreateAdvanceRequest):
    db_advance = Advance(**notification.model_dump())
    db.add(db_advance)
    db.commit()
    db.refresh(db_advance)
    return db_advance

def get_advance_by_user_id(db: Session, id: int):
    return db.query(Advance).filter(Advance.id == id).first()

def get_all_advances(db: Session):
    return db.query(Advance).all()

# def update_notification(db: Session, id: int, notification: NotificationsUpdate, user_id: int):
#     db_notification = get_notification_by_id(db, id)
    
#     if (db_notification.for_all == True):
#         return None
    
#     if not db_notification:
#         return None

#     for field, value in notification.model_dump(exclude_unset=True).items():
#         setattr(db_notification, field, value)

#     db.commit()
#     db.refresh(db_notification)
#     return db_notification

# def delete_notification(db: Session, notification_id: int, user_id:int):
#     db_notification = get_notification_by_id(db, notification_id)

#     if (db_notification.for_all == True):
#         return False
    
#     if not db_notification:
#         return False

#     db.delete(db_notification)
#     db.commit()
#     return True

# def delete_all(db: Session, for_me: list[int]):
#     deleted = db.query(Notifications).filter(
#         Notifications.id.in_(for_me)
#     ).delete(synchronize_session=False)

#     db.commit()
#     return deleted > 0