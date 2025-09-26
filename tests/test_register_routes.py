from fastapi.testclient import TestClient
import httpx
from main import app
import json
import base64
from services.auth import login
from sqlmodel import Session, select
from utils.db import get_engine
from supabase import Client
from utils.supabase import get_supabase_client, get_supabase_admin_client
from schemas.organizations import OrganizationCreated
from models.organization_profile import OrganizationProfile

organization_data = {
    "email": "organization@gmail.com",
    "password": "password",
    "password_confirm": "password",
    "organization_name": "Organization SA de CV",
    "admin_first_name": "Admin",
    "admin_last_name": "Pérez",
    "admin_slast_name": "Ramírez",
    "biography": "Esta es una descripción muy coqueta",
}

client = TestClient(app)
COMPRESSED_IMAGE_ROUTE: str = "./tests/b64encoded_images/test_png_compressed.txt"
ORGANIZATION_REGISTER_ROUTE: str = "/organizations/register"

TEST_EMAIL = "organizationtest@gmail.com" # Asegurarse de tener este usuario registrado en la base de datos de Supabase antes de ejecutar estos tests
TEST_PASSWORD = "password"
TEST_UID = "4112c4c1-9ff9-43a1-b650-c31949c79221" # Se consigue en la tabla de usuarios de Supabase. Debe corresponder al usuario de preubas utilizado para estos tests.

def test_registro_de_organizacion() -> None:
    id_created_organization: str | None = None
    imagen_de_perfil: bytes | None = None
    try:
        with open(COMPRESSED_IMAGE_ROUTE, "r") as f:
            imagen_de_perfil: bytes = base64.b64decode(f.read())
        
        supabase: Client = get_supabase_admin_client()

        files = {
            'organization_data': (None, json.dumps(organization_data), 'application/json'),
            'image': ('profile_photo.png', imagen_de_perfil, 'image/png')
        }

        response: httpx.Response = client.post(
            url=ORGANIZATION_REGISTER_ROUTE,
            files=files
        )

        organization_created: OrganizationCreated = OrganizationCreated(**response.json())
        id_created_organization = str(organization_created.id_user)

        assert response.status_code == 200
        assert organization_created.id_organization is not None
        assert organization_created.organization_name == organization_data["organization_name"]
        assert organization_created.id_user is not None
        assert organization_created.photo_url is not None
        assert organization_created.get_admin_full_name() == f"{organization_data["admin_first_name"]} {organization_data["admin_last_name"]} {organization_data['admin_slast_name']}"
        assert organization_created.biography == organization_data["biography"]
        assert organization_created.jwt is not None

        supabase_response = (
            supabase.storage
            .from_("avatars")
            .list(path="public/organizations")
        )

        assert any(item["name"] == organization_created.photo_url.split('/')[-1] for item in supabase_response)
    
    finally:
        try:
            supabase = get_supabase_admin_client()
            supabase.auth.admin.delete_user(id_created_organization)
            supabase.storage.empty_bucket("avatars")
        except Exception:
            pass

def test_registro_de_organizacion_sin_foto_de_perfil() -> None:
    id_created_organization: int | None = None
    try:        
        supabase: Client = get_supabase_client()

        session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

        files = {
            'organization_data': (None, json.dumps(organization_data), 'application/json')
        }

        response: httpx.Response = client.post(
            url=ORGANIZATION_REGISTER_ROUTE,
            files=files,
            headers={
                "Authorization": f"Bearer {session.access_token}"
            }
        )

        organization: OrganizationProfile = OrganizationProfile(**response.json())
        id_created_organization = organization.id_organization

        assert response.status_code == 200
        assert organization.id_organization is not None
        assert organization.organization_name == organization_data["organization_name"]
        assert organization.id_user is not None
        assert organization.photo_url is not None
        assert organization.get_admin_full_name() == f"{organization_data["admin_first_name"]} {organization_data["admin_last_name"]} {organization_data['admin_slast_name']}"
        assert organization.biography == organization_data["biography"]

        supabase.auth.sign_out()
        
        supabase_response = (
            supabase.storage
            .from_("avatars")
            .list(path="public/organizations")
        )

        assert not supabase_response
    
    finally:
        if id_created_organization is not None:
            with Session(get_engine()) as s:
                stmt = select(OrganizationProfile).where(OrganizationProfile.id_organization == id_created_organization)
                organization: OrganizationProfile = s.exec(stmt).first()
                s.delete(organization)
                s.commit()

def test_registrar_organizacion_sin_ninguno_de_los_campos_opcionales() -> None:
    id_created_organization: int | None = None
    try:
        new_organization: dict = {
            
            "organization_name": organization_data["organization_name"],
            "admin_first_name": organization_data["admin_first_name"],
            "admin_last_name": organization_data["admin_last_name"]
        }

        supabase: Client = get_supabase_client()

        session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

        files = {
            'organization_data': (None, json.dumps(new_organization), 'application/json')
        }

        response: httpx.Response = client.post(
            url=ORGANIZATION_REGISTER_ROUTE,
            files=files,
            headers={
                "Authorization": f"Bearer {session.access_token}"
            }
        )

        organization: OrganizationProfile = OrganizationProfile(**response.json())
        id_created_organization = organization.id_organization

        assert response.status_code == 200
        assert organization.id_organization is not None
        assert organization.organization_name == organization_data["organization_name"]
        assert organization.id_user == TEST_UID
        assert not organization.photo_url
        assert organization.get_admin_full_name() == f"{organization_data["admin_first_name"]} {organization_data["admin_last_name"]}"
        assert not organization.biography

        supabase.auth.sign_out()
        
        supabase_response = (
            supabase.storage
            .from_("avatars")
            .list(path="public/organizations")
        )

        assert not supabase_response
    
    finally:
        if id_created_organization is not None:
            with Session(get_engine()) as s:
                stmt = select(OrganizationProfile).where(OrganizationProfile.id_organization == id_created_organization)
                organization: OrganizationProfile = s.exec(stmt).first()
                s.delete(organization)
                s.commit()

def test_registrar_organizacion_sin_datos_obligatorios() -> None:
    new_organization: dict = {
            "admin_first_name": organization_data["admin_first_name"],
            "admin_slast_name": "Ramírez",
            "biography": "Esta es una descripción muy coqueta",
        }

    supabase: Client = get_supabase_client()

    session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

    files = {
        'organization_data': (None, json.dumps(new_organization), 'application/json')
    }

    response: httpx.Response = client.post(
        url=ORGANIZATION_REGISTER_ROUTE,
        files=files,
        headers={
            "Authorization": f"Bearer {session.access_token}"
        }
    )
    response_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in response_data and "Los datos están incompletos o no cumplen el formato esperado" in response_data["detail"]

def test_registrar_organizacion_con_datos_en_formatos_incorrectos() -> None:
    new_organization: dict = {
            "organization_name": 56,
            "admin_first_name": organization_data["admin_first_name"],
            "admin_last_name": False,
            "admin_slast_name": "Ramírez",
            "biography": "Esta es una descripción muy coqueta",
        }

    supabase: Client = get_supabase_client()

    session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

    files = {
        'organization_data': (None, json.dumps(new_organization), 'application/json')
    }

    response: httpx.Response = client.post(
        url=ORGANIZATION_REGISTER_ROUTE,
        files=files,
        headers={
            "Authorization": f"Bearer {session.access_token}"
        }
    )
    response_data = response.json()

    assert response.status_code == 422
    assert "detail" in response_data and "Los datos están incompletos o no cumplen el formato esperado" in response_data["detail"]

def test_registrar_organizacion_con_imagen_que_excede_el_limite_de_tamanio() -> None:
    imagen_de_perfil: bytes | None = None

    with open("./tests/b64encoded_images/test_png_overweighted.txt", "r") as f:
        imagen_de_perfil: bytes = base64.b64decode(f.read())
    
    supabase: Client = get_supabase_client()

    session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

    files = {
        'organization_data': (None, json.dumps(organization_data), 'application/json'),
        'image': ('profile_photo.png', imagen_de_perfil, 'image/png')
    }

    response: httpx.Response = client.post(
        url=ORGANIZATION_REGISTER_ROUTE,
        files=files,
        headers={
            "Authorization": f"Bearer {session.access_token}"
        }
    )

    response_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in response_data and "Imagen pesa" in response_data["detail"]

    supabase.auth.sign_out()

def test_registrar_organizacion_con_imagen_con_formato_no_valido() -> None:
    imagen_de_perfil: bytes | None = None

    with open("./tests/b64encoded_images/test_gif.txt", "r") as f:
        imagen_de_perfil: bytes = base64.b64decode(f.read())
    
    supabase: Client = get_supabase_client()

    session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

    files = {
        'organization_data': (None, json.dumps(organization_data), 'application/json'),
        'image': ('profile_photo.png', imagen_de_perfil, 'image/png')
    }

    response: httpx.Response = client.post(
        url=ORGANIZATION_REGISTER_ROUTE,
        files=files,
        headers={
            "Authorization": f"Bearer {session.access_token}"
        }
    )

    response_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in response_data and "Formato de imagen no permitido" in response_data["detail"]

    supabase.auth.sign_out()

def test_registrar_organizacion_con_imagen_falsificada() -> None:
    imagen_de_perfil: bytes | None = None

    with open("./tests/b64encoded_images/pdf_con_cabecera_jpg.txt", "r") as f:
        imagen_de_perfil: bytes = base64.b64decode(f.read())
    
    supabase: Client = get_supabase_client()

    session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

    files = {
        'organization_data': (None, json.dumps(organization_data), 'application/json'),
        'image': ('profile_photo.png', imagen_de_perfil, 'image/png')
    }

    response: httpx.Response = client.post(
        url=ORGANIZATION_REGISTER_ROUTE,
        files=files,
        headers={
            "Authorization": f"Bearer {session.access_token}"
        }
    )

    response_data: dict = response.json()

    assert response.status_code == 422
    assert "detail" in response_data and response_data["detail"] == "El archivo enviado no se reconoce como imagen."

    supabase.auth.sign_out()