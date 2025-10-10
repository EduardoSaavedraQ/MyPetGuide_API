from supabase_auth import AuthResponse
from supabase_auth.types import Session
from supabase_auth.errors import AuthApiError
from supabase import Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from typing import Any
from utils.supabase import get_jwks

security = HTTPBearer()

def map_auth_exceptions(e: AuthApiError) -> None:
    """
    Mapea las excepciones del objeto `auth` del cliente de Supabase y devuelve la respuesta HTTP apropiada.

    Args:
        e (supabase_auth.errors.AuthApiError): Excepción lanzada por el objeto auth del cliente de Supabase.

    Raises:
        HTTPExcepction: El código de estado dependerá del `error_code` devuelto en la excepción.
    """
    error_code = getattr(e, "code", None)
    error_message = str(e)

    match(error_code):
        case "user_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se pudo completar el registro con los datos proporcionados."
            )
        case "email_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo ingresado está en espera de ser confirmado."
            )
        case "request_timeout":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio no está disponible por el momento. Intenta más tarde."
            )
        case "bad_json":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Los datos enviados no tienen el formato esperado."
            )
        case "over_email_send_rate_limit":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="El correo ingresado está en espera de ser confirmado."
            )
        case "email_address_invalid":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El correo ingresado no tiene un formato válido. Verifica que incluya '@' y un dominio correcto."
            )
        case _:
            print(f"[AuthError] {error_code=} {error_message=}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado durante el registro. Intenta más tarde."
            )

def signup(credentials: dict, supabase: Client) -> AuthResponse:
    """
    Crea una nueva cuenta a partir de las credenciales proporcionadas.

    Args:
        credentials (dict): Diccionario de credenciales. Debe contener las claves `email` o `phone`, y `password`.
        supabase (supabase.Client): Cliente de Supabase.

    Raises:
        HTTPException: Si se detecta que una cuenta asociada con el correo o el teléfono proporcionados ya existe, se devuelve un error 409 al cliente.
        supabase_auth.error.AuthApiError: Si ocurre un error en el registro de la cuenta mediante el cliente de Supabase.
    """

    response: AuthResponse = supabase.auth.sign_up(credentials)

    if getattr(response, "error", None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.error.message
        )

    if not response.user.identities:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="No se pudo completar el registro con los datos proporcionados."
    )

    return response

def login(email: str, password: str, supabase: Client) -> Session:
    """Autentica a un usuario utilizando su correo y contraseña.

    Esta función intenta iniciar sesión en Supabase con las credenciales
    proporcionadas. Si la autenticación falla (ej. contraseña incorrecta),
    captura el error `AuthApiError` de Supabase y lo convierte en una
    excepción `HTTPException` con código de estado 401 (No autorizado).

    Args:
        email (str): El correo electrónico del usuario que intenta iniciar sesión.
        password (str): La contraseña del usuario.
        supabase (Client): Una instancia activa del cliente de Supabase.

    Raises:
        HTTPException(401): Si las credenciales son inválidas y la autenticación
                            falla en Supabase.

    Returns:
        Session: Un objeto de sesión de Supabase que contiene el token de acceso,
                el token de refresco y la información del usuario autenticado.
    """

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
    """Dependencia de FastAPI para autenticar y validar un JWT de Supabase.

    Esta función actúa como una dependencia de seguridad que se puede inyectar
    en los endpoints que requieren autenticación. Realiza las siguientes acciones:

    1.  Extrae el token JWT del encabezado `Authorization: Bearer`.
    2.  Obtiene el JSON Web Key Set (JWKS) para verificar la firma del token.
    3.  Decodifica y valida el token, incluyendo su firma, audiencia y fecha de expiración.
    4.  Asegura que el payload del token contenga el identificador del usuario (la claim 'sub').

    Si alguna de estas validaciones falla, la función lanza una `HTTPException`
    con un código 401, deteniendo la ejecución de la petición.

    Args:
        token (HTTPAuthorizationCredentials): Las credenciales del token Bearer,
                                            inyectadas automáticamente por FastAPI.

    Raises:
        HTTPException (401): Si el token ha expirado, es inválido, tiene una firma
                            incorrecta, o le falta la claim 'sub'.

    Returns:
        dict[str,Any]: El payload decodificado del JWT, que contiene la
                        información del usuario autenticado.
    """

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
    
def get_user_role(user_uuid: str, supabase: Client) -> str:
    """Determina el rol de un usuario consultando las tablas de perfiles.

    Esta función de utilidad identifica si un UUID de usuario corresponde a un
    'Usuario' normal o a una 'Organización'. Realiza una búsqueda secuencial:
    primero en la tabla `users_profiles` y, si no encuentra un perfil,
    continúa en la tabla `organizations_profiles`.

    Es útil para la lógica de autorización después de que un usuario ha sido
    autenticado para determinar a qué recursos tiene acceso.

    Args:
        user_uuid (str): El UUID del usuario (generalmente extraído de la
                        claim 'sub' del JWT).
        supabase (Client): Una instancia activa del cliente de Supabase para
                        ejecutar las consultas a la base de datos.

    Returns:
        str: La cadena "User" o "Organization" si se encuentra un perfil,
            o una cadena vacía "" si el UUID no existe en ninguna de las dos tablas.
    """

    response = (
        supabase.table("users_profiles")
        .select("id_profile")
        .eq("id_user", user_uuid)
        .execute()
    )

    if response.data:
        return "User"

    response = (
        supabase.table("organizations_profiles")
        .select("id_organization")
        .eq("id_user", user_uuid)
        .execute()
    )

    if response.data:
        return "Organization"
    
    return ""