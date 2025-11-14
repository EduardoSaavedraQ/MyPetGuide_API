from fastapi import HTTPException, status
from sqlmodel import UUID
from storage3.types import UploadResponse
from storage3.exceptions import StorageApiError
from services.image_services import upload_image_to_supabase
from supabase import Client
from postgrest.base_request_builder import APIResponse
from typing import Any

def create_organization_db(
        supabase: Client,
        organization_profile: dict[str, Any],
        id_user: UUID,
        image: bytes | None = None
) -> dict[str, Any]:
    """
    Crea un nuevo registro en la tabla organizations_profiles de Supabase.

    Args:
        supabase (supabase.Client): El cliente de Supabase con el que se accederá a la base de datos.
        organization_profile (dict[str, Any]): Diccionario que contiene los campos que se insertarán en la tabla.
        id_user (UUID): El UUID asociado a la cuenta de la nueva organización.
        image (bytes | None): La imagen (opcional) que aparecerá como foto de perfil de la organización.
    """

    data_to_insert: dict = organization_profile

    data_to_insert["id_user"] = id_user

    response: APIResponse = (
        supabase.table("organizations_profiles")
        .insert(data_to_insert)
        .execute()
    )

    created_organization: dict[str, Any] = response.data[0]

    if image is not None:
        upload_response: UploadResponse = upload_image_to_supabase(
            id=id_user,
            image=image,
            bucket="avatars",
            path="public/organizations",
            supabase=supabase
        )

        update_response: APIResponse = (
            supabase.table("organizations_profiles")
            .update({"photo_url": upload_response.path})
            .eq("id_organization", created_organization["id_organization"])
            .execute()
        )

        created_organization["photo_url"] = upload_response.path

    return created_organization

def update_organization_profile(
        supabase: Client,
        id_user: str,
        profile_data: dict[str, str | None],
        image_profile: bytes | None = None
) -> dict[str, str | None]:
    """Actualiza los datos del perfil de una organización.

    Actualiza el registro del perfil de una organización en la base de datos. De enviarse una foto de perfil,
    se almacena en storage, actualiza también ese campo y elimina la vieja foto asociada.

    Args:
        supabase (Client): Cliente de Supabase con el que se realizan las operaciones de actualización en la base de datos.
        id_user (str): El UUID de la cuenta de la organización.
        profile_data (dic[str,str|None]): Diccionario con los datos de la organización que se actualizarán en la base de datos.
        image_profile (bytes|None): Bytes de la foto de perfil de la organización (opcional).

    Returns:
        dict[str,str|None]: Diccionario con los datos actualizados de la organización.
    """

    response: APIResponse = (
        supabase.table("organizations_profiles")
        .select("id_user", "photo_url")
        .eq("id_user", id_user)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La cuenta de la organización no existe o no tiene un perfil asociado."
        )

    organization_profile_data: dict[str, str] = response.data[0]

    old_photo_url: str | None = organization_profile_data.get("photo_url", None)

    if image_profile is not None:
        upload_response: UploadResponse = upload_image_to_supabase(
            id=id_user,
            image=image_profile,
            bucket="avatars",
            path="public/organizations",
            supabase=supabase
        )

        profile_data["photo_url"] =  upload_response.path

    response = (
        supabase.table("organizations_profiles")
        .update(profile_data)
        .eq("id_user", id_user)
        .execute()
    )

    updated_organization_profile: dict[str, str] = response.data[0]

    if old_photo_url is not None:
        try:
            supabase.storage.from_("avatars").remove([old_photo_url])            
        except StorageApiError:
            pass

    try:
        updated_organization_profile["photo_url"] =  supabase.storage.from_("avatars").create_signed_url(
            path=updated_organization_profile["photo_url"],
            expires_in=3600
        )["signedUrl"]

    except StorageApiError:
        updated_organization_profile["photo_url"] = None

    return updated_organization_profile

def get_organization_all_data(supabase: Client, id_user: str) -> dict[str, Any]:
    """Recopila y estructura todos los datos de una organización y sus mascotas.

    Esta función de servicio obtiene el perfil completo de una organización y la
    lista de todas las mascotas que ha puesto en adopción.

    Una característica clave es que itera sobre la lista de mascotas y convierte
    sus rutas de imágenes (`photo_url`) en **URLs firmadas (signed URLs)** con una
    duración limitada, proporcionando un acceso seguro y temporal a los archivos.

    Args:
        supabase (Client): Instancia del cliente de Supabase para ejecutar las consultas.
        id_user (str): El UUID de la cuenta de usuario asociada a la organización.

    Returns:
        dict[str, Any]: Un diccionario con dos claves: 'organization' (con el perfil
                        de la organización) y 'pets' (una lista de sus mascotas).
                        Las `photo_url` de las mascotas son URLs firmadas temporalmente.
    """

    organization_query_response: APIResponse = (
        supabase.table("organizations_profiles")
        .select("*")
        .eq("id_user", id_user)
        .execute()
    )

    if not organization_query_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Los datos de la organización no fueron encontrados."
        )

    organization_data: dict[str, int | str] = organization_query_response.data[0]

    if organization_data["photo_url"] is not None:
        try:
            organization_data["photo_url"] = supabase.storage.from_("avatars").create_signed_url(
                path=organization_data["photo_url"],
                expires_in=3600
            )
        except StorageApiError:
            organization_data["photo_url"] = None

    pet_query_response = (
        supabase.table("pets")
        .select("*")
        .eq("id_owner", id_user)
        .execute()
    )

    organization_pets: list = pet_query_response.data

    for pet in organization_pets:
        if pet["photo_url"] is not None:
            try:
                pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(
                    path=pet["photo_url"],
                    expires_in=3600
                )
            except StorageApiError:
                pet["photo_url"] = None

    return {
        "organization": organization_data,
        "pets": organization_pets
    }