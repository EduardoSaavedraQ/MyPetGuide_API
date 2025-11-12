from fastapi import HTTPException, status
from sqlmodel import UUID
from storage3.types import UploadResponse
from schemas.users import UserRead
from services.image_services import upload_image_to_supabase
from supabase import Client
from postgrest.base_request_builder import APIResponse
from storage3.exceptions import StorageApiError
from services.ml.kmeans_service import predict_cluster
from utils.user import USER_FEAUTURES_TO_SCALE, USER_BOOL_FEATURES, can_clusterize, transform_bool_cluster_features_to_int
from services.ml.scaler_service import scale_data
from typing import Any

def create_user_db(supabase: Client,
    user_profile: dict[str, Any],
    id_user: UUID,
    image: bytes | None = None
) -> dict[str, Any]:
    """Crea un registro de perfil para un nuevo usuario en la base de datos.

    Inserta los datos del perfil en la tabla `users_profiles`. Si se proporciona
    una imagen, la sube a Supabase Storage y, en una segunda operación, actualiza
    el registro del perfil recién creado con la URL de la foto.

    Args:
        supabase (Client): El cliente de Supabase para acceder a la base de datos.
        user_profile (dict[str, Any]): Diccionario con los campos a insertar.
        id_user (UUID): El UUID de la cuenta de usuario a la que se asocia el perfil.
        image (bytes | None): Opcional, la imagen de perfil del usuario en bytes.

    Returns:
        dict[str, Any]: Un diccionario con los datos del perfil de usuario recién
                        creado, incluyendo la `photo_url` si se subió una imagen.
    """

    data_to_insert: dict = user_profile

    data_to_insert["id_user"] = id_user

    response: APIResponse = (
        supabase.table("users_profiles")
        .insert(data_to_insert)
        .execute()
    )

    created_user: dict[str, Any] = response.data[0]

    if image is not None:
        upload_response: UploadResponse = upload_image_to_supabase(
            id=id_user,
            image=image,
            bucket="avatars",
            path="public/users",
            supabase=supabase
        )

        update_response: APIResponse = (
            supabase.table("users_profiles")
            .update({"photo_url": upload_response.path})
            .eq("id_user", created_user["id_user"])
            .execute()
        )

        created_user["photo_url"] = upload_response.path

    return created_user

def update_user_profile(
    supabase: Client,
    id_user: UUID,
    data_to_update: dict[str, Any],
    image: bytes | None = None
) -> dict[str, Any]:
    """Actualiza un perfil de usuario, su foto y recalcula su etiqueta de clúster.

    Esta función de servicio maneja la actualización de un perfil de usuario. Si se
    proporciona una nueva imagen, sigue un proceso de "subir y luego borrar"
    para reemplazar de forma segura la foto existente en Supabase Storage.

    Además, si se proporcionan suficientes datos de compatibilidad, recalcula
    la etiqueta de clúster (`owner_label`) del usuario usando el modelo K-means.
    Finalmente, actualiza el registro en la base de datos con todos los cambios.

    Args:
        supabase (Client): Instancia del cliente de Supabase.
        id_user (UUID): El UUID del usuario cuyo perfil se va a actualizar.
        data_to_update (dict[str, Any]): Diccionario con los campos a modificar.
        image (bytes | None): Opcional, los bytes de la nueva foto de perfil.

    Returns:
        dict[str, Any]: Un diccionario con los datos del perfil actualizado,
                        directamente desde la respuesta de la base de datos.
    """

    old_photo_path: str | None = None

    if image is not None:

        response_image_field = (
            supabase.table("users_profiles")
            .select("photo_url")
            .eq("id_user", id_user)
            .execute()
        )
        
        if response_image_field.data:
            old_photo_path = response_image_field.data[0].get("photo_url", None)

        upload_response = upload_image_to_supabase(
            id=id_user, image=image, bucket="avatars", path="public/users", supabase=supabase
        )

        data_to_update["photo_url"] = upload_response.path

    if can_clusterize(data_to_update):
        data_to_update = transform_bool_cluster_features_to_int(data_to_update)
        bool_features = [data_to_update[field] for field in USER_BOOL_FEATURES]
        features_to_scale = [data_to_update[field] for field in USER_FEAUTURES_TO_SCALE]
        scaled_data = scale_data("owner", features_to_scale)
        features = scaled_data[0] + bool_features
        cluster = predict_cluster("owner", features)
        data_to_update["owner_label"] = cluster[0]

    response: APIResponse = (
        supabase.table("users_profiles")
        .update(data_to_update)
        .eq("id_user", id_user)
        .execute()
    )

    if old_photo_path is not None:
        supabase.storage.from_("avatars").remove([old_photo_path])

    try:
        response.data[0]["photo_url"] = supabase.storage.from_("avatars").create_signed_url(
            path=response.data[0]["photo_url"],
            expires_in=3600
        )["signedURL"]

    except StorageApiError:
        response.data[0]["photo_url"] = None

    return response.data[0]

def get_user_all_data(supabase: Client, id_user: str) -> dict[str, Any]:
    """Recopila y estructura todos los datos de un usuario, incluyendo perfil y mascotas.

    Esta función obtiene el perfil de un usuario y la lista completa de sus mascotas
    asociadas. Una característica clave es que convierte todas las rutas de imágenes
    (tanto del usuario como de sus mascotas) en URLs firmadas (signed URLs) con una
    duración limitada, proporcionando un acceso seguro y temporal a los archivos.

    Args:
        supabase (Client): Instancia del cliente de Supabase.
        id_user (str): El UUID del usuario cuyos datos se van a recuperar.

    Returns:
        dict[str, Any]: Un diccionario con dos claves: 'user' (que contiene el perfil
                        del usuario) y 'pets' (una lista de sus mascotas). Todas
                        las 'photo_url' son URLs firmadas temporalmente.
    """

    user_query_response: APIResponse = (
        supabase.table("users_profiles")
        .select("*")
        .eq("id_user", id_user)
        .execute()
    )

    if not user_query_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Los datos del usuario no fueron encontrados."
        )

    user_data: dict = user_query_response.data[0]

    if user_data["photo_url"]:
        try:
            user_data["photo_url"] = supabase.storage.from_("avatars").create_signed_url(
                path=user_data["photo_url"],
                expires_in=3600
            )
        except StorageApiError:
            user_data["photo_url"] = None

    pet_query_response = (
        supabase.table("pets")
        .select("*")
        .eq("id_owner", id_user)
        .execute()
    )

    user_pets: list = pet_query_response.data

    for pet in user_pets:
        if pet["photo_url"] is not None:
            try:
                pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(
                    path=pet["photo_url"],
                    expires_in=3600
                )
            except StorageApiError:
                pet["photo_url"] = None

    return {
        "user": user_data,
        "pets": user_pets
    }