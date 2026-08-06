from supabase import AuthApiError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.models.auth_models import User
from src.db.sb_db import supabase


oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str = Depends(oauth2scheme)) -> User:
    try:
        if not token:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="No token")
        user = supabase.auth.get_user(jwt=token)
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
        ) from e
    