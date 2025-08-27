from dotenv import load_dotenv
from supabase import create_client, Client
from supabase_auth.types import AuthResponse
import os
import requests
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Any
import pytest

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")

def test_supabase_jwt_decoding() -> None:
    try:
        key: dict[str, Any] | str = requests.get(SUPABASE_JWKS_URL).json() if os.getenv("APP_ENV") == "production" else os.getenv("JWT_SECRET")

        token: str = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImMzYzRiNGE1LTdiYjYtNDU5My1iMDFkLTgzN2QzNWQyODcyZiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Bid3RpaXFreGh4bWl5dXZna3ZnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMDMwZGZjNS1jZDAwLTRmZTEtYTMzMC0wOWZiZmRkZTg1ZDAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MjQ3NjI0LCJpYXQiOjE3NTYyNDc1ODgsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzU2MjQ3NTg4fV0sInNlc3Npb25faWQiOiJjMjQ5NmU4ZS0yNjRiLTRjNzQtOTViNC1mY2NiYTFkY2Y1M2IiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.NZr5upva-DDY20opwAWfRFO0TqKh2KOAJqhZ58Y9QI_IE9LC22AsPUf3QRTDFC_cf-0OI0hz8m-4B7_XgYPiUw"

        payload: dict[str, Any] = jwt.decode(
            token=token,
            key=key,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_exp": False}
        )

        print(payload)

        assert payload['email'] == "test@test.com"
        assert payload['role'] == "authenticated"
        assert payload['sub'] == "2030dfc5-cd00-4fe1-a330-09fbfdde85d0"  # Verificar subject
        assert 'exp' in payload  # Verificar que existe campo expiración

    except JWTError as e:
        pytest.fail(f"El JWT no fue decodificado con éxito: {str(e)}")

def test_supabase_jwt_is_expired() -> None:
    try:
        jwks: dict[str, Any] = requests.get(SUPABASE_JWKS_URL).json()

        # El siguiente es un token expirado
        token: str = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImMzYzRiNGE1LTdiYjYtNDU5My1iMDFkLTgzN2QzNWQyODcyZiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Bid3RpaXFreGh4bWl5dXZna3ZnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMDMwZGZjNS1jZDAwLTRmZTEtYTMzMC0wOWZiZmRkZTg1ZDAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MjQ4NTU2LCJpYXQiOjE3NTYyNDg1MjAsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzU2MjQ4NTIwfV0sInNlc3Npb25faWQiOiJhY2E1N2MyNy1iY2ZkLTQ2NTktYjI5OC00OTAxMWZjZGQ4Y2EiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.Gu8RZUJVzYij-_bW6pjDcUfHiWL0mADX5XraiCK7vF5IFfagMlO6n5yIKcx5jLdbI5ulFT_ZEuddnCXPo5JHbg"

        payload: dict[str, Any] = jwt.decode(
            token=token,
            key=jwks,
            algorithms=["ES256"],
            audience="authenticated",
        )

        pytest.fail("La decodificación debería lanzar un error porque el token ya ha expirado")

    except ExpiredSignatureError:
        assert True
    except JWTError:
        pytest.fail("Se esperaba un error de expiración, pero ocurrió otro tipo de error al decodificar el JWT")

def test_fresh_supabase_jwt() -> None:

    supabase: Client = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

    try:
        jwks: dict[str, Any] = requests.get(SUPABASE_JWKS_URL).json()

        # Iniciamos sesión con el usuario de prueba previamente registrado para obtener un JWT fresco
        response: AuthResponse = supabase.auth.sign_in_with_password({
            "email": "test@test.com",
            "password": "password"
        })

        # Obtenmos el JWT del usuario recién autenticado
        access_token: str = response.session.access_token

        payload: dict[str, Any] = jwt.decode(
            token=access_token,
            key=jwks,
            algorithms=["ES256"],
            audience="authenticated",
            options={
                "verify_exp": True,
                "verify_aud": True,
                "verify_iat": True
            }
        )

        assert payload['email'] == "test@test.com"
        assert payload['role'] == "authenticated"
        assert 'exp' in payload
        assert 'iat' in payload
        assert 'sub' in payload


    except ExpiredSignatureError:
        pytest.fail("Token fresco no debería estar expirado")
    except JWTError as e:
        pytest.fail(f"Error decodificando token fresco: {str(e)}")
    except Exception as e:
        pytest.fail(f"Error inesperado: {str(e)}")

    finally:
        try:
            supabase.auth.sign_out()
        except:
            pass  # Silenciar errores en logout

def test_invalid_token_signature() -> None:
    """Test para token con firma inválida"""
    jwks: dict[str, Any] = requests.get(SUPABASE_JWKS_URL).json()
    
    # Token modificado (firma inválida)
    invalid_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImMzYzRiNGE1LTdiYjYtNDU5My1iMDFkLTgzN2QzNWQyODcyZiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Bid3RpaXFreGh4bWl5dXZna3ZnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMDMwZGZjNS1jZDAwLTRmZTEtYTMzMC0wOWZiZmRkZTg1ZDAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MjQ3NjI0LCJpYXQiOjE3NTYyNDc1ODgsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzU2MjQ3NTg4fV0sInNlc3Npb25faWQiOiJjMjQ5NmU4ZS0yNjRiLTRjNzQtOTViNC1mY2NiYTFkY2Y1M2IiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.INVALID_SIGNATURE_HERE"
    
    with pytest.raises(JWTError):  # ✅ Debe fallar
        jwt.decode(
            token=invalid_token,
            key=jwks,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_exp": False}
        )