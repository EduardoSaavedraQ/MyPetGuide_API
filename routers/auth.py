from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from supabase_auth.types import Session
from schemas.auth import LoginForm
from utils.supabase import get_supabase_client, get_supabase_admin_client
from services import auth
from typing import Any

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Session)
def login(credentials: LoginForm, supabase: Client = Depends(get_supabase_client)) -> Session:
    """Autentica a un usuario y devuelve una sesión con un token de acceso.

    Verifica las credenciales del usuario (email y contraseña) contra la base
    de datos de Supabase. Si son correctas, devuelve un objeto de sesión que
    incluye el JWT (access_token) necesario para autenticar peticiones a
    rutas protegidas.

    Args:
        credentials (LoginForm): Objeto con `email` y `password` proveniente
                                del cuerpo de la petición.
        supabase (Client): Dependencia para obtener el cliente de Supabase.

    Raises:
        HTTPException (401): Si las credenciales son incorrectas.

    Returns:
        Session: Objeto de sesión de Supabase que contiene el `access_token`.
    """

    return auth.login(email=credentials.email, password=credentials.password, supabase=supabase)

@router.get("/role")
def get_user_role(
    current_user: dict[str, Any] = Depends(auth.get_current_active_user),
    supabase: Client = Depends(get_supabase_admin_client)
) -> dict[str, str]:
    """Obtiene el rol ('User' u 'Organization') del usuario autenticado.

    Este es un endpoint protegido que requiere un token JWT válido. Utiliza el
    identificador del token para buscar en las tablas de perfiles y determinar
    si el usuario es un usuario normal o una organización.

    Args:
        current_user (dict): Dependencia que valida el JWT y devuelve el
                            payload del usuario.
        supabase (Client): Dependencia para obtener el cliente de Supabase.

    Raises:
        HTTPException (401): Si el token JWT no es válido o ha expirado.
        HTTPException (404): Si el usuario autenticado no tiene un perfil
                            asociado en la base de datos.

    Returns:
        dict[str, str]: Un diccionario con la clave "role" y el valor
                        correspondiente ("User" o "Organization").
    """

    user_rol: str = auth.get_user_role(user_uuid=current_user["sub"], supabase=supabase)

    if user_rol == "":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró rol para el usuario."
        )
    
    return {"role": user_rol}