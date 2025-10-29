from supabase import Client
from storage3.exceptions import StorageApiError
from postgrest.base_request_builder import APIResponse
from typing import Any

def cleanup_account(user_id: str, supabase_admin_client: Client) -> None:
    """
    Elimina la cuenta asociada al `user_id` de Supabase.

    Args:
        user_id (str): UUID de la cuenta que se debe eliminar.
        supabase_admin_client (supabse.Client): Cliente que se utilizará para la conexión con Supabase. Es importante que tenga permisos de adminsitrador.
    """
    
    try:
        supabase_admin_client.auth.admin.delete_user(user_id)
    except Exception as e:
        print(f"CRITICAL: Background task failed to delete user {user_id}. Error: {e}")

def get_account_public_profile(
    supabase: Client,
    id_user: str
) -> dict[str, Any] | None:
    """
    Obtiene el perfil público del usuario con el id_user dado.

    Args:
        supabase (Client): Cliente de Supabase.
        id_user (str): UUID del usuario.

    Returns:
        dict[str, str] | None: Diccionario con los datos del perfil público del usuario o None si no existe.
    """

    response: APIResponse = (
        supabase.table("users_profiles")
        .select("id_profile, id_user, first_name, last_name, slast_name, photo_url")
        .eq('id_user', id_user)
        .execute()
    )

    if not response.data:
        response: APIResponse = (
            supabase.table("organizations_profiles")
            .select('*')
            .eq("id_user", id_user)
            .execute()
        )

        if not response.data:
            return None
        
    profile: dict[str, Any] = response.data[0]

    if profile['photo_url']:
        try:
            profile['photo_url'] = supabase.storage.from_("avatars").create_signed_url(
                path=profile['photo_url'],
                expires_in=3600
            )["signedUrl"]

        except StorageApiError:
            profile['photo_url'] = None

    return profile