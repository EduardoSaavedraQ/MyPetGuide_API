from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from utils.supabase import get_supabase_admin_client
from services import pet
from typing import Any
from services import auth

router = APIRouter(prefix="/pets", tags=["pets"])

@router.get("/for-adoption") # Se agrega una 's' que faltaba para que la ruta sea plural
async def get_pets_for_adoption(
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> list[dict[str, Any]]:

    pets = pet.get_all_pets_in_adoption(supabase=supabase, page=page, id_user=current_user["sub"])

    return pets

@router.get("/recommended")
async def get_recommended_pets(
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> list[dict[str, Any]]:
    return pet.get_recommended_pets(supabase=supabase, id_user=current_user["sub"], page=page)

@router.get("/breeds/{species}")
def get_breeds_by_species(
    species: str,
    supabase: Client = Depends(get_supabase_admin_client)
) -> list:

    match(species.lower()):
        case "dog":
            species = True
        case "cat":
            species = False
        case _:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La especie debe ser 'dog' o 'cat'."
            )

    breeds = (
        supabase.table("breeds")
        .select("id_breed, breed_name")
        .eq("species", species)
        .execute()
    )

    return breeds.data