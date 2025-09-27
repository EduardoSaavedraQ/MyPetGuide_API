from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from supabase import Client, AuthApiError
from utils.supabase import get_supabase_client, get_supabase_admin_client
from schemas.users import UserCreate, UserRead, UserCreated
from exceptions.image_exceptions import ImageSizeLimitExceeded, InvalidImageFormat
from PIL import UnidentifiedImageError
from services import auth
from services.user import create_user_db
import json

router = APIRouter(prefix="/users", tags=["users"])

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
