from fastapi import APIRouter, Depends
from supabase import Client
from postgrest.base_request_builder import APIResponse
from utils.supabase import get_supabase_admin_client
from services.auth import get_current_active_user
from schemas.chat import ChatCreate, ChatRead
from typing import Any

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/create", response_model=ChatRead)
async def create_chat_room(
    identifiers: ChatCreate,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict[str, Any] = Depends(get_current_active_user)
) -> dict[str, Any]:

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