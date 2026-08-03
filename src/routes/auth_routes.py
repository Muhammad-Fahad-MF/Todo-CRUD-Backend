from fastapi import APIRouter, HTTPException, status
from src.models.auth_models import SignupReq
from src.db.sb_db import supabase


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup")
async def signup(payload: SignupReq):
    response = supabase.auth.sign_up({
        "email": payload.email,
        "password": payload.password,
        "options": {
            "data": {
                "display_name": payload.name
            }
        }
    })
    if not response:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Sign up failed!")
    
    return {
        "user_id": response.user.id,
        "email": response.user.email,
        "full_name": response.user.user_metadata.get("full_name")
    }


@router.post("/login")
async def login(payload: )
