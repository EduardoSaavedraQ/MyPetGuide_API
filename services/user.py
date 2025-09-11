from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from supabase_auth.errors import AuthApiError
import os
from jose import jwt, ExpiredSignatureError, JWTError
from typing import Any
import httpx
from async_lru import alru_cache

security = HTTPBearer()

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
    

async def get_current_active_user(
        token: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    
    try:
        jwks = await get_jwks()

        payload = jwt.decode(
            token=token.credentials,
            key=jwks,
            algorithms=["ES256"],
            audience="authenticated",
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "verify_iss": False
            }
        )

        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta 'sub'"
            )

        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )
    
def sign_in(email: str, password: str) -> dict[str, Any]:
    supabase: Client = create_client(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_ANON_KEY")
    )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error en autenticación: Credenciales inválidas"
        )
    
    return response.session