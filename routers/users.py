from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from supabase import Client, AuthApiError
from utils.supabase import get_supabase_client, get_supabase_admin_client
from schemas.users import UserCreate, UserRead, UserCreated, UserProfileCreate
from exceptions.image_exceptions import ImageSizeLimitExceeded, InvalidImageFormat
from PIL import UnidentifiedImageError
from services import auth
from services.user import create_user_db, update_user_profile
from typing import Any
import json

router = APIRouter(prefix="/user", tags=["users"])

@router.post("/register", response_model=UserCreated)
async def create_user(
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase_anon_client: Client = Depends(get_supabase_client),
    supabase_admin_client: Client = Depends(get_supabase_admin_client)
) -> UserCreated:
    try:
        image_bytes: bytes | None = None

        if image is not None:
            image_bytes = await image.read()

        profile_data_dict: dict = json.loads(data)
        user_profile: UserCreate = UserCreate(**profile_data_dict)

        sign_up_reponse = auth.signup(credentials=user_profile.model_dump(include={"email", "password"}), supabase=supabase_anon_client)

        user_profile: UserRead = create_user_db(supabase=supabase_admin_client, user_profile=user_profile, id_user=sign_up_reponse.user.id, image=image_bytes)

        user_created: UserCreated = UserCreated(**user_profile.model_dump())

        user_created.jwt = sign_up_reponse.session.access_token

        return user_created
    
    except (json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de JSON de organización no válido: {e}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Los datos están incompletos o no cumplen el formato esperado: {e}"
        )

    except (InvalidImageFormat, ImageSizeLimitExceeded) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    except UnidentifiedImageError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo enviado no se reconoce como imagen."
        )

@router.get("/profile", response_model=UserRead)
async def get_user_profile(
    supabase_anon_client: Client = Depends(get_supabase_client)
) -> UserRead:
    try:
        user = auth.get_current_user(supabase=supabase_anon_client)

        response = (
            supabase_anon_client.table("users_profiles")
            .select("*")
            .eq("id_user", user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró el perfil del usuario."
            )

        user_profile: UserRead = UserRead(**response.data[0])

        return user_profile

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/profile")
async def create_user_profile(profile_data: UserProfileCreate, supabase: Client = Depends(get_supabase_admin_client), current_user: dict[str, Any] = Depends(auth.get_current_active_user)) -> dict[str, str]:
    try:
        update_user_profile(supabase=supabase, id_user=current_user['sub'], data_to_update=profile_data.model_dump(exclude_unset=True))

        return {"message": "Perfil de usuario creado"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Los datos están incompletos o no cumplen el formato esperado: {e}"
        )