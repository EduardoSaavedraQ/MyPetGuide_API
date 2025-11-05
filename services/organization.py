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

    organization_data: dict = organization_query_response.data[0]

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