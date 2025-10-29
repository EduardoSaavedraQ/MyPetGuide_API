from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from utils.supabase import get_supabase_admin_client
from services import auth, account_services
from typing import Any, Union
from schemas.users import UserPublicInfo
from schemas.organization import OrganizationRead

router = APIRouter(tags=["public-profile"])

@router.get("/public-profile/{id_user}", response_model=Union[UserPublicInfo, OrganizationRead])
async def get_user_public_profile(
    id_user: str,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    """Obtiene el perfil público del usuario autenticado.

    Este endpoint protegido recupera la información pública del perfil del
    usuario que realiza la petición. Esta información puede ser vista por otros
    usuarios de la plataforma.

    Args:
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict): Dependencia que valida el JWT y devuelve el
                            payload del usuario.

    Raises:
        HTTPException (401): Si el token JWT no es válido o ha expirado.

    Returns:
        dict[str, Any]: Un objeto JSON con el perfil público del usuario.
    """

    user_public_profile = account_services.get_account_public_profile(
        supabase=supabase,
        id_user=id_user
    )

    if user_public_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario solicitado no tiene un perfil público o no existe."
        )

    return user_public_profile