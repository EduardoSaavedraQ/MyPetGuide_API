from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client, AuthApiError
from supabase_auth import AuthResponse
from schemas.auth import SignUpForm
from utils.supabase import get_supabase_client
from services.auth import map_auth_exceptions

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=AuthResponse)
def signup(credentials: SignUpForm, supabase: Client = Depends(get_supabase_client)) -> AuthResponse:
    try:
        response: AuthResponse = supabase.auth.sign_up(credentials.model_dump(include={"email", "password"}))

        if getattr(response, "error", None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error.message
            )
        
        if not response.user.identities:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo completar el registro con los datos proporcionados."
        )
        
        return response
    
    except AuthApiError as e:
        map_auth_exceptions(e)