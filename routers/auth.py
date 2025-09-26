from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from supabase_auth import AuthResponse
from schemas.auth import SignUpForm, LoginForm
from utils.supabase import get_supabase_client, get_supabase_admin_client
from services import auth
from typing import Any

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=AuthResponse)
def signup(credentials: SignUpForm, supabase: Client = Depends(get_supabase_client)) -> AuthResponse:
    return auth.signup(credentials=credentials.model_dump(include={"email", "password"}), supabase=supabase)

@router.post("/login")
def login(credentials: LoginForm, supabase: Client = Depends(get_supabase_client)):
    return auth.login(email=credentials.email, password=credentials.password, supabase=supabase)

@router.get("/role/")
def get_user_role(
    current_user: dict[str, Any] = Depends(auth.get_current_active_user),
    supabase: Client = Depends(get_supabase_admin_client)
) -> dict[str, str]:
    user_rol: str = auth.get_user_role(user_uuid=current_user["sub"], supabase=supabase)

    if user_rol == "":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró rol para el usuario."
        )
    
    return {"role": user_rol}