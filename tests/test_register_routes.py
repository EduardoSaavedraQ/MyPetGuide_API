from fastapi.testclient import TestClient
import httpx
from main import app
import json
import base64
from services.auth import login
from models.organization_profile import OrganizationProfile
from sqlmodel import Session, select
from utils.db import get_engine
from supabase import Client
from utils.supabase import get_supabase_client

organization_data = {
    "id": None,
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
    id_created_organization: int | None = None
    imagen_de_perfil: bytes | None = None
    try:
        with open(COMPRESSED_IMAGE_ROUTE, "r") as f:
            imagen_de_perfil: bytes = base64.b64decode(f.read())
        
        supabase: Client = get_supabase_client()

        session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

        files = {
            'organization_data': (None, json.dumps(organization_data), 'aplication/json'),
            'image': ('profile_photo.png', imagen_de_perfil, 'image/png')
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
        assert organization.photo_url is not None
        assert organization.get_admin_full_name() == f"{organization_data["admin_first_name"]} {organization_data["admin_last_name"]} {organization_data['admin_slast_name']}"
        assert organization.biography == organization_data["biography"]

        supabase.auth.sign_out()

        supabase_response = (
            supabase.storage
            .from_("avatars")
            .list(path="public/organizations")
        )

        assert any(item["name"] == organization.photo_url.split('/')[-1] for item in supabase_response)
    
    finally:
        if id_created_organization is not None:
            with Session(get_engine()) as s:
                stmt = select(OrganizationProfile).where(OrganizationProfile.id_organization == id_created_organization)
                organization: OrganizationProfile = s.exec(stmt).first()
                s.delete(organization)
                s.commit()

                supabase: Client = get_supabase_client()

                supabase.storage.empty_bucket("avatars")

def test_registro_de_organizacion_sin_foto_de_perfil() -> None:
    id_created_organization: int | None = None
    try:        
        supabase: Client = get_supabase_client()

        session = login(email=TEST_EMAIL, password=TEST_PASSWORD, supabase=supabase)

        files = {
            'organization_data': (None, json.dumps(organization_data), 'aplication/json')
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