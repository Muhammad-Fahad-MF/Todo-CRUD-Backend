from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from src.models.auth_models import User
from src.routes.deps import security, verify_token, HTTPAuthorizationCredentials


router = APIRouter(prefix="/data")


@router.get("/public/info")
def get_public_data():
    return {"public_data": "It is public"}


@router.get("/protected/info")
def get_protected_data(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    if not token.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token")
    return {"private_data": "This data is private"}


@router.get("/protected/profile")
def get_profile(user: Annotated[User, Depends(verify_token)]):
    return user


@router.get("/protected/dashboard")
def get_dashboard(user: Annotated[User, Depends(verify_token)]):
    return {"Data": "Dashboard"}
