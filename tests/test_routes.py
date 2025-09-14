from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from supabase import Client
from supabase_auth.types import Session
from services.auth import login
from utils.supabase import get_supabase_client
import pytest

TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "password"
TOKEN_EXPIRADO = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImMzYzRiNGE1LTdiYjYtNDU5My1iMDFkLTgzN2QzNWQyODcyZiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Bid3RpaXFreGh4bWl5dXZna3ZnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMDMwZGZjNS1jZDAwLTRmZTEtYTMzMC0wOWZiZmRkZTg1ZDAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MjQ4NTU2LCJpYXQiOjE3NTYyNDg1MjAsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzU2MjQ4NTIwfV0sInNlc3Npb25faWQiOiJhY2E1N2MyNy1iY2ZkLTQ2NTktYjI5OC00OTAxMWZjZGQ4Y2EiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.Gu8RZUJVzYij-_bW6pjDcUfHiWL0mADX5XraiCK7vF5IFfagMlO6n5yIKcx5jLdbI5ulFT_ZEuddnCXPo5JHbg"
TOKEN_CON_FIRMA_INVALIDA = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImMzYzRiNGE1LTdiYjYtNDU5My1iMDFkLTgzN2QzNWQyODcyZiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Bid3RpaXFreGh4bWl5dXZna3ZnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMDMwZGZjNS1jZDAwLTRmZTEtYTMzMC0wOWZiZmRkZTg1ZDAiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MjQ3NjI0LCJpYXQiOjE3NTYyNDc1ODgsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzU2MjQ3NTg4fV0sInNlc3Npb25faWQiOiJjMjQ5NmU4ZS0yNjRiLTRjNzQtOTViNC1mY2NiYTFkY2Y1M2IiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.INVALID_SIGNATURE_HERE"

def test_ruta_protegida_de_prueba_usuario_autenticado_de_prueba() -> None:
    client = TestClient(app)

    supabase: Client = get_supabase_client()

    try:
        supabase_response: Session = login(TEST_EMAIL, TEST_PASSWORD)

        fastapi_response = client.get("/protegida", headers={
            "Authorization": f"Bearer {supabase_response.access_token}"
        })

        assert fastapi_response.status_code == 200
        assert fastapi_response.json().get("mensaje") == f"Hola, test@test.com"

    except HTTPException as http_exc:
        pytest.fail(f"HTTPException durante la prueba: {str(http_exc.detail)}")

    except Exception as e:
        pytest.fail(f"Error inesperado durante la prueba: {str(e)}")

    finally:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

def test_ruta_protegida_de_prueba_sin_token() -> None:
    client = TestClient(app)

    response = client.get("/protegida")

    assert response.status_code == 403  # 403 Forbidden por falta de credenciales
    assert response.json().get("detail") == "Not authenticated"

def test_ruta_protegida_de_prueba_con_token_invalido() -> None:
    client = TestClient(app)

    response = client.get("/protegida", headers={
        "Authorization": "Bearer token_invalido"
    })

    assert response.status_code == 401
    assert "Token inválido" in response.json().get("detail")

def test_ruta_protegida_de_prueba_con_token_expirado() -> None:
    client = TestClient(app)

    response = client.get("/protegida", headers={
        "Authorization": f"Bearer {TOKEN_EXPIRADO}"
    })

    # Token JWT expirado (generado previamente y conocido)
    assert response.status_code == 401
    assert "Token expirado" in response.json().get("detail")

def test_ruta_protegida_de_prueba_con_token_con_firma_invalida() -> None:
    client = TestClient(app)

    response = client.get("/protegida", headers={
        "Authorization": f"Bearer {TOKEN_CON_FIRMA_INVALIDA}"
    })

    assert response.status_code == 401
    assert "Token inválido" in response.json().get("detail")

def test_login_exitoso() -> None:
    client = TestClient(app)

    response = client.post("/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json().get("token_type") == "bearer"

def test_login_fallido_contraseña_incorrecta() -> None:
    client = TestClient(app)

    response = client.post("/login", json={
        "email": TEST_EMAIL,
        "password": "badpassword"
    })

    assert response.status_code == 401
    assert response.json().get("detail") == "Error en autenticación: Credenciales inválidas"