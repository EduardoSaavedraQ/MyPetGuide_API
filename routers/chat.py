from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from postgrest.base_request_builder import APIResponse
from utils.supabase import get_supabase_admin_client
from services.auth import get_current_active_user
from services.chat import get_user_chats
from schemas.chat import ChatCreate, ChatCreated, ChatReadIncomming, ChatReadOutcomming, ChatRead
from typing import Any, List

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/create", response_model=ChatCreated)
async def create_chat_room(
    identifiers: ChatCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(get_current_active_user)
) -> dict[str, int | str]:
    """Crea una nueva sala de chat en la base de datos.

    Utiliza los identificadores de la mascota que se quiere adoptar, el que solicita adoptarla
    y el del dueño actual de la mascota.

    Args:
        identifiers (ChatCreate): Contendor y validador para los ids de la mascota y el dueño actual
                                    de ésta.
        supabase (Client): Cliente de Supabase mediante el cual se crea el registro en la base de datos.
        current_user (dict[str, int | str]): Diccionario de los datos del usuario que solicita adoptar
                                            la mascota. Obtenido del JWT contenido en la cabecera Authorization.

    Returns:
        dict[str,int|str]: Diccionario con los datos registrados en la tabla `chat_room` en la base de datos.
    """

    response: APIResponse = (
        supabase.table("chat_rooms")
        .insert({
            "id_pet": identifiers.id_pet,
            "id_requester": current_user["sub"],
            "id_owner": identifiers.id_owner
        })
        .execute()
    )

    return response.data[0]

@router.get("/incomming", response_model=List[ChatReadIncomming])
async def get_incomming_chat_rooms_for_user(
    finished: bool = False,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(get_current_active_user)
) -> list[dict[int | dict[str, Any]]]:
    """Obtiene las salas de chat donde el usuario actual es el dueño de la mascota.

    Recupera todas las salas de chat donde el usuario autenticado es el dueño de la mascota
    que otro usuario quiere adoptar. Los chats pueden filtrarse por su estado (finalizados o activos).

    Args:
        finished (bool, optional): Filtro para obtener chats finalizados (True) o activos (False).
                                    Por defecto es False.
        supabase (Client): Cliente de Supabase para consultar la base de datos.
        current_user (dict[str, Any]): Datos del usuario autenticado obtenidos del JWT.

    Returns:
        list[dict[int | dict[str, Any]]]: Lista de salas de chat con la información de la mascota
                                            y del usuario solicitante (requester).
    """

    chats: list = get_user_chats(
        supabase=supabase,
        user_identifier=current_user["sub"],
        incomming=True,
        finished=finished
    )

    return chats

@router.get("/outcomming", response_model=List[ChatReadOutcomming])
async def get_outcomming_chat_rooms_for_user(
    finished: bool = False,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(get_current_active_user)
) -> list[dict[int | dict[str, Any]]]:
    """Obtiene las salas de chat donde el usuario actual es el solicitante.

    Recupera todas las salas de chat donde el usuario autenticado es quien solicita
    adoptar una mascota. Los chats pueden filtrarse por su estado (finalizados o activos).

    Args:
        finished (bool, optional): Filtro para obtener chats finalizados (True) o activos (False).
                                    Por defecto es False.
        supabase (Client): Cliente de Supabase para consultar la base de datos.
        current_user (dict[str, Any]): Datos del usuario autenticado obtenidos del JWT.

    Returns:
        list[dict[int | dict[str, Any]]]: Lista de salas de chat con la información de la mascota
                                            y del dueño actual de la mascota (owner).
    """

    chats: list = get_user_chats(
        supabase=supabase,
        user_identifier=current_user["sub"],
        incomming=False,
        finished=finished
    )

    return chats

@router.patch("/finish/{id_chat}", response_model=ChatCreated)
async def finish_chat_room(
    id_chat: int,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(get_current_active_user)
):
    """
    Marca una sala de chat como finalizada si el usuario autenticado es requester u owner.

    - id_chat (int): id de la sala a finalizar.
    - Acceso permitido solo si current_user["sub"] coincide con id_requester o id_owner.
    - Retorna el registro actualizado (modelo ChatCreated). Lanza 404 si no se encontró o no tiene acceso.
    """
    user_id = current_user["sub"]

    chat_finished_response: APIResponse = (
        supabase.table("chat_rooms")
        .update({"finished": True})
        .eq("id_chat", id_chat)
        .or_(f"id_requester.eq.{user_id},id_owner.eq.{user_id}")
        .execute()
    )

    if not chat_finished_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or access denied")

    return chat_finished_response.data[0]