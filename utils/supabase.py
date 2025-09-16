from supabase import create_client, Client
import httpx
from async_lru import alru_cache
from typing import Any
from fastapi import HTTPException, status
import os

def get_supabase_client(admin: bool = False) -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") if admin else os.getenv("SUPABASE_ANON_KEY")
    return create_client(supabase_url, supabase_key)

@alru_cache(maxsize=1, ttl=3600)
async def get_jwks() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=os.getenv("SUPABASE_JWKS_URL"),
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error conectando con Supabase: {str(e)}"
        )