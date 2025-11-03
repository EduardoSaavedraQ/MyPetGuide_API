from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from postgrest.base_request_builder import APIResponse
from services.auth import get_current_active_user
from utils.supabase import get_supabase_admin_client
from schemas.adoption import AdoptionCreate
from typing import Any

router = APIRouter(prefix="adoption/")

@router.post("/transfer-pet-ownership")
async def transfer_pet_ownership(
    adoption_data: AdoptionCreate,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    supabase: Client = Depends(get_supabase_admin_client)
) -> dict[str, str]:
    """Transfiere la propiedad de una mascota de un usuario a otro.

    Verifica que que la mascota especificada por su id esté presente en la base de datos y que sí
    sea propiedad del usuario autenticado. Además, verifica que el usuario que solicita la adopción
    también esté presente en la BD.

    Args:
        adoption_data

    Raises:
        HTTPException (400): Si el id del usuario que solicita la adopción y el del usuario autenticado
                            son exactamene el mismo.
        HTTPException (404): Si la mascota o el usuario que solicita la adopción no están presentes
        en la BD.

    Returns:
        dict[str,str]: Mensaje de confirmación del éxito de la adopción.
    """

    if adoption_data.id_requester == current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los identificadores de los usuarios involucrados en la adopción no deben coincidir."
        )

    pet_response: APIResponse = (
        supabase.table("pets")
        .select("id_pet")
        .eq("id_pet", adoption_data.id_pet)
        .eq("id_owner", current_user["sub"])
        .limit(1)
        .execute()
    )

    if not pet_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró a la mascota con los identificadores proporcionados."
        )

    requester_response: APIResponse = (
        supabase.table("auth.users")
        .select("id")
        .eq("id", adoption_data.id_requester)
        .limit(1)
        .execute()
    )

    if not requester_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario adoptante no fue encontrado con el identificador proporcionado."
        )

    try:
        supabase.rpc(
            "transfer_pet_ownership",
            {
                "pet_id": adoption_data.id_pet,
                "new_owner": adoption_data.id_requester
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al dar en adopción a la mascota.\n{str(e)}"
        )

    return {"message": "Adopción exitosa"}