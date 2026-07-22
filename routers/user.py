from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud.users as userss
from db import get_db
from auth.userAuthentication import get_current_user_id
from schemas import SignupRequest
import bcrypt

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post('/create')
async def post_user_profile(body: SignupRequest, db: Session = Depends(get_db)):
    user = None

    try:
        # Hash password
        user_hash_pass = await hash_password(body)

        user = userss.create_user(db, user_hash_pass)
        
    except:
        print("Something went wrong when getting user")
        user = None

    return {"result": user, "success": bool(user)}

async def hash_password(user_:SignupRequest) -> SignupRequest:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_["password"].encode("utf-8"), salt)

    user_["password"] = hashed_password.decode("utf-8")
    return user_