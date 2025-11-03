from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from supabase import Client
from utils.supabase import get_supabase_admin_client
from utils.image_utils import validate_image
from schemas.pet import PetCreate, PetReadWithPetLabel
from services import pet
from services import auth
from exceptions.image_exceptions import ImageTooLarge, InvalidImageFormat, NoImageFormatFound
from PIL import UnidentifiedImageError
from typing import Any
import json


router = APIRouter(prefix="/pet", tags=["pet"])

@router.post("/register", response_model=PetReadWithPetLabel)
async def create_pet(
    data: str = Form(...),
    image: UploadFile | None = File(None),
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(auth.get_current_active_user)
) -> dict[str, Any]:
    """Registra una nueva mascota en el sistema, asociándola al usuario autenticado.

    Este endpoint maneja la creación de un nuevo perfil de mascota. Utiliza un
    formato `multipart/form-data` para aceptar tanto los datos del perfil en
    formato JSON como una imagen opcional. El endpoint está protegido y requiere
    autenticación.

    La petición debe contener los siguientes campos de formulario:
    - **data**: Una cadena de texto (string) que contiene un objeto JSON con
                todos los detalles de la mascota, conforme al modelo `PetCreate`.
    - **image**: Un archivo de imagen opcional para el perfil de la mascota.

    Args:
        data (str): Campo de formulario que contiene un JSON string con los
                    datos del perfil de la mascota.
        image (UploadFile | None): Campo de formulario opcional que contiene el
                                archivo de imagen de la mascota.
        supabase (Client): Dependencia para obtener el cliente de Supabase.
        current_user (dict): Dependencia que valida el JWT y devuelve los datos
                            del usuario autenticado.

    Raises:
        HTTPException (400): Si la cadena en el campo `data` no es un JSON válido.
        HTTPException (422): Si la imagen es inválida (formato, tamaño) o si los
                            datos del JSON no pasan la validación del modelo `PetCreate`.
        HTTPException (401): Si el token JWT no es proporcionado o no es válido.
        HTTPException (500): Si ocurre un error inesperado durante el registro
                            en la base de datos.

    Returns:
        dict[str, Any]: Un objeto JSON con el perfil completo de la mascota recién
                        creada, conforme al modelo `PetReadWithPetLabel`.
    """

    image_bytes: bytes | None = None
    created_pet: dict[str, Any] | None = None

    ##########################################
    # Sección de validación de entradas
    ##########################################
    try:
        if image is not None:
            image_bytes = await image.read()

            validate_image(image_bytes)

        pet__data_dict: dict = json.loads(data)
        pet_profile: PetCreate = PetCreate(**pet__data_dict)

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
    ##########################################

    ##########################################
    # Sección de registro de mascota
    ##########################################
    try:
        created_pet = pet.create_pet(
            data=pet_profile.model_dump(),
            image=image_bytes,
            id_user=current_user["sub"],
            supabase=supabase
        )

        return created_pet
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar a la mascota. Error: {e}"
        )
