from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, BackgroundTasks
from supabase import Client, AuthApiError
from supabase_auth import AuthResponse
from utils.supabase import get_supabase_client, get_supabase_admin_client
from utils.image_utils import validate_image
from schemas.users import UserCreate, UserRead, UserCreated, UserProfileCreate, UserProfileUpadate
from exceptions.image_exceptions import ImageTooLarge, InvalidImageFormat, NoImageFormatFound
from PIL import UnidentifiedImageError
from services import auth, account_services
from services.user import create_user_db, update_user_profile as update_user_profile_service, get_user_all_data
from typing import Any
import json
from pydantic_core import PydanticCustomError

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/register", response_model=UserCreated)
async def create_user(
    background_task: BackgroundTasks,
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase_anon_client: Client = Depends(get_supabase_client),
    supabase_admin_client: Client = Depends(get_supabase_admin_client)
) -> dict[str, Any]:
    """
    Registra un nuevo usuario normal en el sistema.

    Esta ruta realiza las siguientes acciones:
    - Valida y decodifica los datos JSON enviados en el campo `data`.
    - Opcionalmente valida una imagen enviada como archivo.
    - Crea un nuevo usuario en Supabase con las credenciales proporcionadas.
    - Inserta el perfil del usuario en la base de datos.
    - Devuelve los datos del usuario creado junto con un token JWT.

    Args:
        - data (str): Cadena JSON con los datos del usuario. Debe incluir campos como
        `email`, `password`, `password_confirm`, `first_name`, `last_name`, etc.
        - image (UploadFile | None): Imagen opcional que representa al usuario.
        - supabase_anon_client (Client): Cliente Supabase para operaciones de autenticación.
        - supabase_admin_client (Client): Cliente Supabase con privilegios administrativos.

    Errores posibles:
    - 400 BAD REQUEST: Si el JSON enviado en `data` no tiene el formato correcto.
    - 422 UNPROCESSABLE ENTITY: Si la imagen es inválida, demasiado grande, o no se reconoce como imagen.
    - 422 UNPROCESSABLE ENTITY: Si los datos del usuario están incompletos o mal formateados.

    Retorna:
    - dict[str, Any]: Diccionario con los datos del usuario creado y el token JWT.
    """

    image_bytes: bytes | None = None
    sign_up_reponse: AuthResponse | None = None
    created_user: dict[str, Any] | None = None

    ##########################################
    # Sección de validación de entradas
    ##########################################
    try:
        if image is not None:
            image_bytes = await image.read()

            validate_image(image=image_bytes)

        user_data_dict: dict = json.loads(data)
        user_data: UserCreate = UserCreate(**user_data_dict)

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
    # Sección de registro de usuario
    ##########################################
    try:
        sign_up_reponse = auth.signup(
            credentials=user_data.model_dump(include={"email", "password"}),
            supabase=supabase_anon_client
        )

        fields_to_insert_in_users_profiles_table: dict[str, str] = user_data.model_dump(include={
            "first_name", "last_name", "slast_name"
        })

        created_user = create_user_db(
            supabase=supabase_admin_client,
            user_profile=fields_to_insert_in_users_profiles_table,
            id_user=sign_up_reponse.user.id,
            image=image_bytes
        )

        created_user["jwt"] = sign_up_reponse.session.access_token
        created_user["refresh_token"] = sign_up_reponse.session.refresh_token

        return created_user

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

@router.post("/profile")
async def create_user_profile(
    profile_data: UserProfileCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, str]:
    """Crea el perfil de compatibilidad del usuario autenticado.

    Este endpoint permite a un usuario normal registrado completar su
    perfil, que son utilizados por el sistema de recomendación de mascotas.

    Args:
        profile_data (UserProfileCreate): Cuerpo de la petición con los datos del
                                        perfil a crear o actualizar.
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict[str,Any]): Dependencia que valida el JWT y devuelve los datos
                            del usuario autenticado.

    Raises:
        HTTPException (422): Si los datos proporcionados no cumplen con el formato
                            o las validaciones esperadas.
        HTTPException (401): Si el token JWT no es válido o ha expirado.

    Returns:
        dict[str, str]: Un mensaje de confirmación de que la operación fue exitosa.
    """

    try:
        update_user_profile_service(supabase=supabase, id_user=current_user['sub'], data_to_update=profile_data.model_dump(exclude_unset=True))

        return {"message": "Perfil de usuario creado"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Los datos están incompletos o no cumplen el formato esperado: {e}"
        )

@router.put("/profile", response_model=UserRead)
async def update_user_profile(
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    """Endpoint para editar la información del perfil del usuario.

    Permite la actualización de perfil de un usuario normal. Valida que los datos recibidos
    y la imagen estén en el formato corracto. Devuelve la información del perfil actualizada
    al cliente.

    Args:
        data (str): String en formato JSON que contiene la información que se va a actualizar en la
                    base de datos.
        image (UploadFile|None): Imagen de perfil opcional.
        supabase (Cliente): Cliente de Supabase con el que se realizarán las operaciones de actualización
                            de la base de datos.
        current_user (dict): Dependencia que valida el JWT y devuelve los datos
                            del usuario autenticado.

    Raises:
        HTTPException (400): Si el campo `data` no tiene un formato JSON válido.
        HTTPException (401): Si el token JWT no es válido o ha expirado.
        HTTPException (422): Si los datos proporcionados no cumplen con el formato
                            o las validaciones esperadas.

    Returns:
        dict[str,Any]: Los datos actualizados del perfil del usuario directos desde
                        la base de datos que indican la confirmación de los cambios.
    """

    image_bytes: bytes | None = None

    try:
        if image is not None:
            image_bytes = await image.read()

        user_profile_new_data: UserProfileUpadate = UserProfileUpadate(**json.loads(data))

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

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Los datos están incompletos o no cumplen el formato esperado: {e}"
        )

    user_profile_updated: dict[str, Any] = update_user_profile_service(
        supabase=supabase,
        id_user=current_user["sub"],
        data_to_update=user_profile_new_data.model_dump(),
        image=image_bytes
    )

    return user_profile_updated

@router.get("/all-data")
async def get_all_user_data(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    """Obtiene todos los datos del perfil del usuario autenticado.

    Este endpoint protegido recupera la información completa del perfil del
    usuario que realiza la petición. Combina los datos almacenados en la
    base de datos (nombre, preferencias, mascotas, etc.) con la información del token
    de autenticación (como el correo electrónico).

    Args:
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict): Dependencia que valida el JWT y devuelve el
                            payload del usuario.

    Raises:
        HTTPException (401): Si el token JWT no es válido o ha expirado.

    Returns:
        dict[str, Any]: Un objeto JSON con el perfil completo del usuario.
    """

    user_data = get_user_all_data(supabase=supabase, id_user=current_user['sub'])
    user_data["email"] = current_user["email"]

    return user_data