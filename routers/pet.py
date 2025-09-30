from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from supabase import Client
from utils.supabase import get_supabase_admin_client
from schemas.pets import PetCreate
from services import pet
from services import auth
from exceptions.image_exceptions import ImageSizeLimitExceeded, InvalidImageFormat
from PIL import UnidentifiedImageError
from typing import Any
import json


router = APIRouter(prefix="/pet", tags=["pets"])

@router.post("/register")
async def create_pet(
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    try:
        image_bytes: bytes | None = None

        if image is not None:
            image_bytes = await image.read()

        pet_profile_dict: dict = json.loads(data)
        pet_profile_dict: PetCreate = PetCreate(**pet_profile_dict)

        created_pet = pet.create_pet(data=pet_profile_dict.model_dump(), image=image_bytes, id_user=current_user["sub"], supabase=supabase)

        return created_pet

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

@router.get("s/for-adoption") # Se agrega una 's' que faltaba para que la ruta sea plural
async def get_pets_for_adoption(
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> list[dict[str, Any]]:
    
    pets = pet.get_all_pets_in_adoption(supabase=supabase, page=page, id_user=current_user["sub"])

    return pets

@router.get("s/recommended")
async def get_recommended_pets(
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> list[dict[str, Any]]:
    return pet.get_recommended_pets(supabase=supabase, id_user=current_user["sub"], page=page)