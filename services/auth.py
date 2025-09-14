from supabase_auth.types import Session
from supabase_auth.errors import AuthApiError
from supabase import Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from typing import Any
from utils.supabase import get_supabase_client, get_jwks

security = HTTPBearer()

def login(email: str, password: str) -> Session:
    supabase: Client = get_supabase_client()

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