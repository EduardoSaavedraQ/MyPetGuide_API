from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from utils.supabase import get_supabase_admin_client
from services import pet
from typing import Any
from services import auth
from schemas.breed import BreedRead
from schemas.pet import PetRead, PetReadWithPetLabel
from typing import List

router = APIRouter(prefix="/pets", tags=["pets"])

@router.get("/for-adoption", response_model=List[PetRead])
async def get_pets_for_adoption(
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> list[dict[str, Any]]:
    """Obtiene una lista paginada de mascotas disponibles para adopción.

    Este endpoint protegido devuelve un listado de mascotas que están actualmente
    marcadas como 'en proceso de adopción'. Requiere autenticación.

    Args:
        page (int | None): Parámetro de consulta opcional para la paginación de resultados.
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict): Dependencia que valida el JWT y devuelve el payload
                            del usuario autenticado.

    Returns:
        list[dict[str, Any]]: Una lista con los perfiles de las mascotas en adopción.
    """

    pets = pet.get_all_pets_in_adoption(supabase=supabase, page=page, id_user=current_user["sub"])

    return pets

@router.get("/recommended", response_model=List[PetReadWithPetLabel])
async def get_recommended_pets(
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> list[dict[str, Any]]:
    """Obtiene una lista paginada de mascotas recomendadas para el usuario.

    Utiliza el perfil del usuario autenticado para encontrar y devolver una lista
    de mascotas que son altamente compatibles con su estilo de vida y preferencias,
    basado en el sistema de recomendación.

    Args:
        page (int | None): Parámetro de consulta opcional para la paginación.
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict): Dependencia que valida el JWT y obtiene los datos del
                            usuario para el que se calculará la recomendación.

    Returns:
        list[dict[str, Any]]: Una lista con los perfiles de las mascotas compatibles.
    """

    return pet.get_recommended_pets(supabase=supabase, id_user=current_user["sub"], page=page)

@router.get("/breeds/{species}", response_model=List[BreedRead])
def get_breeds_by_species(
    species: str,
    supabase: Client = Depends(get_supabase_admin_client)
) -> list:
    """Obtiene un listado de razas para una especie específica (perro o gato).

    Este endpoint público es útil para poblar selectores o menús desplegables
    en la interfaz de usuario, permitiendo a los usuarios filtrar o registrar
    mascotas por su raza. No requiere autenticación.

    Args:
        species (str): Parámetro de ruta que especifica la especie.
                       **Valores permitidos:** "dog" o "cat".

    Raises:
        HTTPException (400): Si el valor de `species` no es "dog" ni "cat".

    Returns:
        list: Una lista de objetos, donde cada objeto contiene el `id_breed` y
            el `breed_name` de una raza.
    """

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
        .select('*')
        .eq("species", species)
        .execute()
    )

    return breeds.data