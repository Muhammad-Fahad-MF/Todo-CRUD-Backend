from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.db.sb_db import supabase
from src.models.auth_models import User
from supabase import AuthApiError

router = APIRouter(prefix= "/data")

oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2scheme)) -> User:
    try:
        if not token:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="No token")
        user = supabase.auth.get_user(jwt=token)
        print(user)
        if not user:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        return User(
            id= user.user.id,
            name= user.user.user_metadata.get("display_name"),
            email= user.user.email,
            created_at= user.user.created_at
        )
    except AuthApiError as e:
        raise HTTPException(
            status_code= e.status,
            detail= e.message
        )
    except Exception as e:
        print(f"VERIFY_TOKEN FAILED: {repr(e)}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "Internal Server error"
        )

@router.get("/public/info")
def get_public_data():
    return {"public_data": "It is public"}


@router.get("/protected/info")
def get_protected_data(token: Annotated[str, Depends(oauth2scheme)]):
    if not token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="No token")
    return {"private_data": "This data is private"}


@router.get("/protected/profile")
def get_profile(user: Annotated[User, Depends(verify_token)]):
    return user
