from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from schemas.organizations import OrganizationCreate, OrganizationRead
from models.organization_profile import OrganizationProfile
from services.organization import create_organization_db
from services.auth import get_current_active_user
from supabase import Client
from utils.supabase import get_supabase_client
from exceptions.image_exceptions import ImageSizeLimitExceeded, InvalidImageFormat
import json
from typing import Any
from PIL import UnidentifiedImageError

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/register", response_model=OrganizationRead)
async def create_organization(
    organization_data: str = Form(...),
    image: UploadFile | None = File(None),
    current_user: dict[str, Any] = Depends(get_current_active_user),
    supabase: Client = Depends(get_supabase_client)
) -> OrganizationProfile:
    try:
        image_bytes: bytes | None = None
        
        if image is not None:
            image_bytes = await image.read()

        profile_data_dict: dict = json.loads(organization_data)
        organization_profile: OrganizationCreate = OrganizationCreate(**profile_data_dict)

        return create_organization_db(supabase=supabase, organization_profile=organization_profile, user_id=current_user.get("sub"), image=image_bytes)
    
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