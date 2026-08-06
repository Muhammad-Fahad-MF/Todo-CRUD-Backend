from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from supabase import AuthApiError
from src.db.sb_db import supabase
from src.models.auth_models import SignupReq, LoginReq
from src.routes.deps import security, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
async def signup(payload: SignupReq):
    try:
        response = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {
                    "data": {
                        "display_name": payload.name  # Stored as display_name
                    }
                },
            }
        )

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

        return {
            "user_id": response.user.id,
            "email": response.user.email,
            "display_name": response.user.user_metadata.get("display_name"),
        }

    except AuthApiError as e:
        # Supabase client errors (e.g. "User already registered" returns e.status=400)
        raise HTTPException(
            status_code=e.status or status.HTTP_400_BAD_REQUEST, detail=e.message
        ) from e


@router.post("/login")
async def login(payload: LoginReq):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

        return {
            "user_id": response.user.id,
            "email": response.user.email,
            "display_name": response.user.user_metadata.get("display_name"),
            "access_token": response.session.access_token,
        }

    except AuthApiError as e:
        raise HTTPException(
            status_code=e.status or status.HTTP_400_BAD_REQUEST, detail=e.message
        ) from e


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    try:
        supabase.auth.admin.sign_out(token.credentials, scope="local")
    except AuthApiError as e:
        raise HTTPException(
            status_code=e.status or status.HTTP_400_BAD_REQUEST, detail=e.message
        ) from e
