from supabase import Client
from postgrest.base_request_builder import APIResponse
from typing import Any

def get_user_chats(
    supabase: Client,
    user_identifier: str | None = None,
    incomming: bool = True,
    finished: bool = False
) -> list[dict[int | dict[str, Any]]]:

    """Obtiene los chats del usuario correspondientes a las solicitudes de adopción enviadas o recibidas.

    Args:
        supabase (Client): Cliente de Supabase mediante el cual se realizan las consultas a la base
                            de datos y se obtiene la urls firmadas para las fotos de perfil.
        user_identifier (str): UUID del usuario cuyos chats se quieren obtener.
        incomming (bool): Determine si los chats deben corresponder a las solicitudes recibidas (True)
                            o enviadas (False). Valor por defecto: True.
        finished (bool): Permite filtrar por chats finalizados (True) o sin finalizar (False). Valor por
                            defecto: False.

    Returns:
        list[dict,int|dict[str,Any]]: Lista de diccionarios que contienen la información de los chats
                                            solicitados, la mascota solicitada y el otro usuario participante.
    """

    chats_response: APIResponse = (
        supabase.table("chat_rooms")
        .select("id_room, pet:id_pet(id_pet, pet_name, photo_url), id_requester, id_owner")
        .eq("id_owner" if incomming else "id_requester", user_identifier)
        .eq("finished", finished)
        .execute()
    )

    if chats_response.data:
        for chat in chats_response.data:

            try:
                chat["pet"]["photo_url"] = (
                    supabase.storage.from_("avatars")
                    .create_signed_url(
                        path=chat["pet"]["photo_url"],
                        expires_in=3600
                    )
                )

            except Exception:
                chat["pet"]["photo_url"] = None

            profiles_response: APIResponse = (
                supabase.table("users_profiles")
                .select("id_profile, id_user, first_name, last_name, slast_name, photo_url")
                .eq("id_user", chat["id_requester"] if incomming else chat["id_owner"])
                .execute()
            )

            if not profiles_response.data:

                profiles_response = (
                    supabase.table("organizations_profiles")
                    .select('*')
                    .eq("id_user", chat["id_requester"] if incomming else chat["id_owner"])
                    .execute()
                )

            if profiles_response.data:
                try:
                    profiles_response.data[0]["photo_url"] = (
                        supabase.storage.from_("avatars").
                        create_signed_url(
                            path=profiles_response.data[0]["photo_url"],
                            expires_in=3600
                        )
                    )

                except Exception:
                    profiles_response.data[0]["photo_url"] = None

                chat["requester" if incomming else "owner"] = profiles_response.data[0]

    return chats_response.data