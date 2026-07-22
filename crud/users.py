from sqlalchemy.orm import Session
from models import User
from schemas import SignupRequest
import bcrypt

def create_user(db: Session, user: SignupRequest):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id:str):
    return db.query(User).filter(User.id == user_id).all()

def authenticate_user(db: Session, user_info: LoginInfo):
    user = db.query(User).filter(User.username == user_info.username).first()
    authenticated = False
    if (not user): return

    # authenticated = user.password == user_info.password
    authenticated = decrypt_n_auth(user.password, user_info.password)
    if (authenticated): return user
    else: return

def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    for field, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True

# ...

async def decrypt_n_auth(password1: str, password2: str):
    auth = bcrypt.checkpw(password1.encode("utf-8"), password2.encode("utf-8"))
    if auth: return True 
    else: return False