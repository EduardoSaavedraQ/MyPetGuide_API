from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends, BackgroundTasks  
from schemas.organization import OrganizationCreate, OrganizationRead, OrganizationCreated
from services.organization import create_organization_db, get_organization_all_data
from supabase import Client
from supabase_auth import AuthResponse
from supabase_auth.errors import AuthApiError
from utils.supabase import get_supabase_client, get_supabase_admin_client
from utils.image_utils import validate_image
from exceptions.image_exceptions import ImageTooLarge, InvalidImageFormat, NoImageFormatFound
import json
from PIL import UnidentifiedImageError
from services import auth, account_services
from typing import Any
from pydantic_core import PydanticCustomError

router = APIRouter(prefix="/organization", tags=["organization"])

@router.post("/register", response_model=OrganizationCreated)
async def create_organization(
    background_task: BackgroundTasks,
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase_anon_client: Client = Depends(get_supabase_client),
    supabase_admin_client: Client = Depends(get_supabase_admin_client)
) -> dict[str, Any]:
    """
    Registra una nueva organización en el sistema.

    Esta ruta realiza las siguientes acciones:
    - Valida y decodifica los datos JSON enviados en el campo `data`.
    - Opcionalmente valida una imagen enviada como archivo.
    - Crea un nuevo usuario en Supabase con las credenciales proporcionadas.
    - Inserta el perfil de la organización en la base de datos.
    - Devuelve los datos de la organización creada junto con un token JWT.

    Args:
        - data (str): Cadena JSON con los datos de la organización. Debe incluir campos como
        `email`, `password`, `password_confirm`, `organization_name`, `admin_first_name`, etc.
        - image (UploadFile | None): Imagen opcional que representa a la organización.
        - supabase_anon_client (Client): Cliente Supabase para operaciones de autenticación.
        - supabase_admin_client (Client): Cliente Supabase con privilegios administrativos.

    Errores posibles:
    - 400 BAD REQUEST: Si el JSON enviado en `data` no tiene el formato correcto.
    - 422 UNPROCESSABLE ENTITY: Si la imagen es inválida, demasiado grande, o no se reconoce como imagen.
    - 422 UNPROCESSABLE ENTITY: Si los datos de la organización están incompletos o mal formateados.

    Retorna:
    - dict[str, Any]: Diccionario con los datos de la organización creada y el token JWT.
    """

    image_bytes: bytes | None = None
    sign_up_reponse: AuthResponse | None = None
    created_organization: dict[str, Any] | None = None

    ##########################################
    # Sección de validación de entradas
    ##########################################
    try:
        if image is not None:
            image_bytes = await image.read()

            validate_image(image=image_bytes)

        organization_data_dict: dict = json.loads(data)
        organization_data: OrganizationCreate = OrganizationCreate(**organization_data_dict)

    except (json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de JSON no válido: {e}"
        )

    except (InvalidImageFormat, ImageTooLarge, NoImageFormatFound) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    except UnidentifiedImageError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo enviado no se reconoce como imagen."
        )
    
    except PydanticCustomError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message_template
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Los datos están incompletos o no cumplen el formato esperado: {e}"
        )
    ##########################################       

    ##########################################
    # Sección de registro de organización
    ##########################################
    try:
        sign_up_reponse = auth.signup(
            credentials=organization_data.model_dump(include={"email", "password"}),
            supabase=supabase_anon_client
        )

        fields_to_insert_in_organizations_profiles_table: dict[str, str] = organization_data.model_dump(include={
            "organization_name", "admin_first_name", "admin_last_name", "admin_slast_name", "biography"
        })

        created_organization = create_organization_db(
            supabase=supabase_admin_client,
            organization_profile=fields_to_insert_in_organizations_profiles_table,
            id_user=sign_up_reponse.user.id,
            image=image_bytes
        )

        created_organization["jwt"] = sign_up_reponse.session.access_token
        created_organization["refresh_token"] = sign_up_reponse.session.refresh_token

        return created_organization

    except AuthApiError as e:
        auth.map_auth_exceptions(e)

    except Exception as e:

        # Limpiar el usuario si se llegó a crear sin un perfil de organización.
        if sign_up_reponse:
            background_task.add_task(
                account_services.cleanup_account,
                sign_up_reponse.user.id,
                supabase_admin_client
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la cuenta. Error: {e}"
        )

@router.get("/all-data")
async def get_all_user_data(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    """Obtiene todos los datos del perfil de la organización.

    Este endpoint protegido recupera la información completa del perfil del
    de la organización del usuario que realiza la petición. Combina los datos almacenados en la
    base de datos (nombre de la organización, nombre de administrador, mascotas, etc.) con la información del token
    de autenticación (como el correo electrónico).

    Args:
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict): Dependencia que valida el JWT y devuelve el
                            payload del usuario.

    Raises:
        HTTPException (401): Si el token JWT no es válido o ha expirado.

    Returns:
        dict[str, Any]: Un objeto JSON con el perfil completo de la organización.
    """

    organization_data = get_organization_all_data(supabase=supabase, id_user=current_user['sub'])
    organization_data["email"] = current_user["email"]

    return organization_data