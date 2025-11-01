from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from postgrest.base_request_builder import APIResponse
from utils.supabase import get_supabase_admin_client
from services.auth import get_current_active_user
from services.chat import get_user_chats
from schemas.chat import ChatCreate, ChatCreated, ChatReadIncomming, ChatReadOutcomming
from typing import Any, List

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/create", response_model=ChatCreated)
async def create_chat_room(
    identifiers: ChatCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(get_current_active_user)
) -> dict[str, int | str]:

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
) -> list[dict, int | dict[str, Any]]:

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
) -> list[dict, int | dict[str, Any]]:

    chats: list = get_user_chats(
        supabase=supabase,
        user_identifier=current_user["sub"],
        incomming=False,
        finished=finished
    )

    return chats