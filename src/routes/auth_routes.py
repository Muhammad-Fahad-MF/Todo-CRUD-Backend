from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from supabase import AuthApiError
from supabase_auth import AuthResponse
from src.db.sb_db import supabase
from src.models.auth_models import SignupReq, SignupRes, LoginReq, LoginRes
from src.routes.deps import security, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
async def signup(payload: SignupReq):
    try:
        response: AuthResponse = supabase.auth.sign_up(
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

        return SignupRes(
            user_id=response.user.id,
            email=str(response.user.email),
            display_name=str(response.user.user_metadata.get("display_name"))
        )

    except AuthApiError as e:
        # Supabase client errors (e.g. "User already registered" returns e.status=400)
        raise HTTPException(
            status_code=e.status or status.HTTP_400_BAD_REQUEST, detail=e.message
        ) from e


@router.post("/login")
async def login(payload: LoginReq):
    try:
        response: AuthResponse = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

        session = response.session
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login failed: missing session",
            )

        return LoginRes(
            user_id=response.user.id,
            email=str(response.user.email),
            display_name=str(response.user.user_metadata.get("display_name")),
            access_token=session.access_token,
        )

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
