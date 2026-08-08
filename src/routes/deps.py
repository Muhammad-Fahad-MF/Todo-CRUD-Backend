from supabase import AuthApiError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from src.models.auth_models import User
from src.db.sb_db import supabase


security = HTTPBearer()


def verify_token(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    try:
        if not token.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No token"
            )
        user = supabase.auth.get_user(jwt=token.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )
        return User(
            id=user.user.id,
            name=user.user.user_metadata.get("display_name"),
            email=str(user.user.email),
            created_at=user.user.created_at,
        )
    except AuthApiError as e:
        raise HTTPException(status_code=e.status, detail=e.message) from e
