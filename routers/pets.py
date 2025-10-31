from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from postgrest.base_request_builder import APIResponse
from utils.supabase import get_supabase_admin_client
from services import pet
from typing import Any
from services import auth, pet
from schemas.breed import BreedRead
from schemas.pet import PetRead, PetReadWithPetLabel, CompatiblePetClusters
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
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
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

@router.get('/compatible-groups', response_model=CompatiblePetClusters)
def get_compatible_pet_clusters(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, list[int | float | str]]:
    """
    Calcula y devuelve los clusters de mascotas compatibles para el usuario autenticado.

    Extrae los features del perfil del usuario desde la tabla `users_profiles`
    usando `ORDERED_USER_FEATURES` y delega el cálculo de compatibilidad a
    `services.pet.get_compatible_pet_clusters`.

    Args:
        supabase (Client): Cliente de Supabase (dependencia).
        current_user (dict): Payload del JWT del usuario autenticado (dependencia).

    Returns:
        CompatiblePetClusters: Objeto (modelo de respuesta) que contiene:
            - clusters: lista de identificadores de cluster (int).
            - probabilities: lista de probabilidades/puntuaciones (float) ordenadas.
            - features: (opcional) lista de nombres de features usadas en la predicción.
            - metadata: (opcional) información adicional sobre la predicción.

    Raises:
        HTTPException (404): Si no se encuentra el perfil del usuario en la base de datos.

    Notes:
        - Esta ruta no realiza paginación ni filtrado: devuelve la predicción/estado
        de compatibilidad (clusters) para el usuario actual.
        - El formato exacto devuelto está definido por el modelo `CompatiblePetClusters`.
    """

    from utils.user import ORDERED_USER_FEATURES

    fields: str = ""

    for field in ORDERED_USER_FEATURES:
        fields += field + ','

    fields += "preferred_species"

    response: APIResponse = (
        supabase.table("users_profiles")
        .select(fields)
        .eq("id_user", current_user["sub"])
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el perfil del usuario especificado."
        )

    user_features: dict = response.data[0]

    return pet.get_compatible_pet_clusters(user_features)

@router.get("/pets_by_cluster", responde_model=List[PetReadWithPetLabel])
def get_pets_by_pet_cluster(
    cluster: int,
    page: int | None = None,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)

) -> list[dict[str, Any]]:
    """
    Devuelve mascotas pertenecientes a un cluster específico.

    Recupera las mascotas asignadas al cluster indicado (campo `pet_label`)
    excluyendo las mascotas cuyo dueño sea el usuario que realiza la petición.
    Soporta paginación mediante el parámetro `page` (1-based). La consulta y
    la lógica de negocio se delegan a `services.pet.get_pets_by_pet_cluster`.

    Args:
        cluster (int): Identificador del cluster cuya lista de mascotas se solicita.
                        Es un parámetro obligatorio; FastAPI validará su presencia y tipo.
        page (int | None): Página de resultados (opcional). Si se proporciona,
                            la función de servicio aplicará el paginado.
        supabase (Client): Cliente de Supabase inyectado por dependencia.
        current_user (dict[str, Any]): Payload del JWT del usuario autenticado.

    Raises:
        HTTPException 401/403: Producidas por la dependencia de autenticación si el usuario no está autorizado.
        HTTPException 400: Posible respuesta si `page` es inválido (delegado al servicio).
        HTTPException 404: Si no se encuentran mascotas (según implementación del servicio).

    Returns:
        list[dict[str, Any]] (response_model=List[PetReadWithPetLabel]):
            Lista de objetos que representan mascotas con su etiqueta de cluster.
            El esquema de cada elemento está definido por `PetReadWithPetLabel`.
    """
    pets: list[dict[str, Any]] = pet.get_pets_by_pet_cluster(
        supabase=supabase,
        id_user=current_user["sub"],
        cluster=cluster,
        page=page
    )

    return pets