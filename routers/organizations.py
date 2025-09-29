from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from schemas.organizations import OrganizationCreate,OrganizationRead, OrganizationCreated
from services.organization import create_organization_db, get_organization_all_data
from supabase import Client
from utils.supabase import get_supabase_client, get_supabase_admin_client
from exceptions.image_exceptions import ImageSizeLimitExceeded, InvalidImageFormat
import json
from PIL import UnidentifiedImageError
from services import auth
from typing import Any

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/register", response_model=OrganizationCreated)
async def create_organization(
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase_anon_client: Client = Depends(get_supabase_client),
    supabase_admin_client: Client = Depends(get_supabase_admin_client)
) -> OrganizationCreated:
    try:
        image_bytes: bytes | None = None
        
        if image is not None:
            image_bytes = await image.read()

        profile_data_dict: dict = json.loads(data)
        organization_profile: OrganizationCreate = OrganizationCreate(**profile_data_dict)

        sign_up_reponse = auth.signup(credentials=organization_profile.model_dump(include={"email", "password"}), supabase=supabase_anon_client)

        organization_profile: OrganizationRead = create_organization_db(supabase=supabase_admin_client, organization_profile=organization_profile, id_user=sign_up_reponse.user.id, image=image_bytes)

        organization_created: OrganizationCreated = OrganizationCreated(**organization_profile.model_dump())

        organization_created.jwt = sign_up_reponse.session.access_token
        
        return organization_created
    
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

@router.get("/all-data")
async def get_all_user_data(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    
    organization_data = get_organization_all_data(supabase=supabase, id_user=current_user['sub'])
    organization_data["email"] = current_user["email"]

    return organization_data