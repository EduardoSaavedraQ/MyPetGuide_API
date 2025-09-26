from fastapi.testclient import TestClient
import httpx
from main import app
from email_validator import validate_email, EmailNotValidError
from supabase import Client
from utils.supabase import get_supabase_client
from uuid import uuid4

client = TestClient(app)

sign_up_url: str = "/auth/signup"
login_url: str = "/auth/login"

USER_TEST_EMAIL = "test@test.com"
ORGANIZATION_TEST_EMAIL = "organizationtest@gmail.com"
TEST_PASSWORD = "password"

def test_crear_cuenta() -> None:
    valid_email_generated: bool = False
    fake_email: str = ""

    while(not valid_email_generated):
        try:
            fake_email = f"fake_email_{uuid4().hex[:6]}@gmail.com"
            validate_email(fake_email)
            valid_email_generated = True
        except EmailNotValidError:
            continue
        
    fake_credentials: dict = {
        "email": fake_email,
        "password": "password",
        "password_confirm": "password"
    }

    response: httpx.Response = client.post(url=sign_up_url, json=fake_credentials)

    json_data: dict = response.json()

    try:
        assert response.status_code == 200
        assert "user" in json_data and json_data["user"]["id"] is not None and json_data["user"]["email"] == fake_email
        assert "session" in json_data and json_data["session"] is None
    
    finally:
        supabase: Client = get_supabase_client()
        
        supabase.auth.admin.delete_user(id=json_data["user"]["id"])

def test_crear_cuenta_con_correo_pendiente_de_verificacion_que_acaba_de_registrarse() -> None:
    valid_email_generated: bool = False
    fake_email: str = ""

    while(not valid_email_generated):
        try:
            fake_email = f"fake_email_{uuid4().hex[:6]}@gmail.com"
            validate_email(fake_email)
            valid_email_generated = True
        except EmailNotValidError:
            continue

    fake_credentials: dict = {
        "email": fake_email,
        "password": "password",
        "password_confirm": "password"
    }

    response: httpx.Response = client.post(url=sign_up_url, json=fake_credentials)

    json_data: dict = response.json()

    try:
        assert response.status_code == 200
        assert "user" in json_data and json_data["user"]["id"] is not None and json_data["user"]["email"] == fake_email
        assert "session" in json_data and json_data["session"] is None

        response: httpx.Response = client.post(url=sign_up_url, json=fake_credentials)

        json_data2 = response.json()

        assert response.status_code == 429
        assert "detail" in json_data2
        assert json_data2["detail"] == "El correo ingresado está en espera de ser confirmado."

    finally:
        supabase: Client = get_supabase_client()
        supabase.auth.admin.delete_user(id=json_data["user"]["id"])

def test_crear_cuenta_con_un_correo_ya_registrado_en_supabase() -> None:
    
    test_json: dict = {
        "email": "test@gmail.com", #Usuario de prueba previamente registrado y verificado en Supabase
        "password": "password",
        "password_confirm": "password"
    }

    response: httpx.Response = client.post(
        url=sign_up_url,
        json=test_json
    )

    json_response: dict = response.json()

    assert response.status_code == 409
    assert "detail" in json_response and json_response["detail"] == "No se pudo completar el registro con los datos proporcionados."

def test_crear_cuentas_con_correos_con_formato_no_valido() -> None:
    fake_credentials1: dict = {
        "email": "jkdkfsdajfajfdaf", #Formato de correo no válido para Pydantic
        "password": "password",
        "password_confirm": "password"
    }

    fake_credentials2: dict = {
        "email": "test2@test.com", #Correo no válido para Supabase
        "password": "password",
        "password_confirm": "password"
    }

    response: httpx.Response = client.post(
        url=sign_up_url,
        json=fake_credentials1
    )

    json_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in json_data
    assert "type" in json_data["detail"][0] and json_data["detail"][0]["type"] == "value_error"
    assert "loc" in json_data["detail"][0] and "email" in json_data["detail"][0]["loc"]

    response = client.post(
        url=sign_up_url,
        json=fake_credentials2
    )

    json_data = response.json()

    assert response.status_code == 422
    assert "detail" in json_data and json_data["detail"] == "El correo ingresado no tiene un formato válido. Verifica que incluya '@' y un dominio correcto."

def test_crear_cuenta_con_password_no_valido() -> None:
    fake_credentials: dict = {
        "email": "test2@test.com", #Correo no válido para Supabase
        "password": "password",
        "password_confirm": "password564"
    }

    response: httpx.Response = client.post(
        url=sign_up_url,
        json=fake_credentials
    )

    json_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in json_data
    assert "type" in json_data["detail"][0] and json_data["detail"][0]["type"] == "passwords_mismatch"
    assert "msg" in json_data["detail"][0] and json_data["detail"][0]["msg"] == "Las contraseñas no coinciden"

def test_crear_cuenta_sin_el_campo_password_confirm() -> None:
    fake_credentials: dict = {
        "email": "test2@test.com", #Correo no válido para Supabase
        "password": "password"
    }

    response: httpx.Response = client.post(
        url=sign_up_url,
        json=fake_credentials
    )

    json_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in json_data
    assert "type" in json_data["detail"][0] and json_data["detail"][0]["type"] == "missing"

def test_login_exitoso() -> None:
    client = TestClient(app)

    response = client.post(login_url, json={
        "email": USER_TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json().get("token_type") == "bearer"

def test_login_fallido_contraseña_incorrecta() -> None:
    client = TestClient(app)

    response = client.post(login_url, json={
        "email": USER_TEST_EMAIL,
        "password": "badpassword"
    })

    assert response.status_code == 401
    assert response.json().get("detail") == "Error en autenticación: Credenciales inválidas"

def test_obtener_rol_de_cuenta_de_organizacion() -> None:
    client = TestClient(app)

    login_response = client.post(login_url, json={
        "email": ORGANIZATION_TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    access_token: str = login_response.json()["access_token"]

    role_response = client.get(url="auth/role", headers={
        "Authorization": f"Bearer {access_token}"
    })

    json_data: dict = role_response.json()

    assert role_response.status_code == 200
    assert "role" in json_data and json_data["role"] == "Organization"

def test_obtener_rol_de_cuenta_de_usuario_normal() -> None:
    client = TestClient(app)

    login_response = client.post(login_url, json={
        "email": USER_TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    access_token: str = login_response.json()["access_token"]

    role_response = client.get(url="auth/role", headers={
        "Authorization": f"Bearer {access_token}"
    })

    json_data: dict = role_response.json()

    assert role_response.status_code == 200
    assert "role" in json_data and json_data["role"] == "User"

def test_obtener_rol_de_cuenta_sin_rol() -> None:
    client = TestClient(app)

    login_response = client.post(login_url, json={
        "email": "test@gmail.com",
        "password": TEST_PASSWORD
    })

    access_token: str = login_response.json()["access_token"]

    role_response = client.get(url="auth/role", headers={
        "Authorization": f"Bearer {access_token}"
    })

    json_data: dict = role_response.json()

    assert role_response.status_code == 404
    assert "detail" in json_data and json_data["detail"] == "No se encontró rol para el usuario."