from fastapi import APIRouter, Depends
from supabase import Client
from supabase_auth import AuthResponse
from schemas.auth import SignUpForm, LoginForm
from utils.supabase import get_supabase_client
from services import auth

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=AuthResponse)
def signup(credentials: SignUpForm, supabase: Client = Depends(get_supabase_client)) -> AuthResponse:
    return auth.signup(credentials=credentials.model_dump(include={"email", "password"}), supabase=supabase)

@router.post('/login')
def login(credentials: LoginForm, supabase: Client = Depends(get_supabase_client)):
    return auth.login(email=credentials.email, password=credentials.password, supabase=supabase)
