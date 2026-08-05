from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.db.sb_db import supabase
from supabase import AuthApiError

router = APIRouter(prefix= "/data")

oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/public/info")
def get_public_data():
    return {"public_data": "It is public"}


@router.get("/protected/info")
def get_protected_data(token: Annotated[str, Depends(oauth2scheme)]):
    if not token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="No token")
    return {"private_data": "This data is private"}


@router.get("/protected/profile")
def get_profile(token: Annotated[str, Depends(oauth2scheme)]):
    try:
        if not token:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="No token")
        access = supabase.auth.get_user(jwt=token)
        if not access:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        return {
            "user_name": access.user.user_metadata.get("display_name"),
            "id": access.user.id,
            "email": access.user.email,
            "created_at": access.user.created_at
        }
    except AuthApiError as e:
        raise HTTPException(
            status_code= e.status,
            detail= e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "Internal Server error"
        )