from supabase import Client

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