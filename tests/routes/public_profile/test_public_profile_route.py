from fastapi.testclient import TestClient
from supabase import Client
from supabase_auth.types import AuthResponse
from utils.supabase import get_supabase_admin_client
from postgrest.base_request_builder import APIResponse
from main import app
import httpx
import pytest

client = TestClient(app)

@pytest.mark.parametrize(
    ("profiles_table", "fields"),
    [
        ("users_profiles", "id_profile, id_user, photo_url, first_name, last_name, slast_name"),
        ("organizations_profiles", '*')
    ],
    ids=["perfiles-usuarios", "perfiles-organizaciones"]
)
def test_get_public_profile_route_devuelve_exitosamente_los_perfiles_publicos_de_las_cuentas_registradas(
    profiles_table: str,
    fields: str
) -> None:
    supabase: Client = get_supabase_admin_client()

    profiles_query_response: APIResponse = (
        supabase.table(profiles_table)
        .select(fields)
        .execute()
    )

    if not profiles_query_response.data:
        pytest.skip("No hay perfiles de cuentas en la base de datos para probar.")

    login_response: AuthResponse = supabase.auth.sign_in_with_password({
        "email": "test@test.com",
        "password": "password"
    })

    if not login_response.session:
        pytest.skip("No se pudo iniciar sesión con el usuario de prueba.")

    try:
        for profile in profiles_query_response.data:
            account_id: str = str(profile["id_user"])

            response: httpx.Response = client.get(
                url=f"/public-profile/{account_id}",
                headers={"Authorization": f"Bearer {login_response.session.access_token}"}
            )

            assert response.status_code == 200

            response_data: dict = response.json()

            for key, value in profile.items():
                if key == "photo_url" and value is not None:
                    assert isinstance(response_data[key], str)
                else:
                    assert response_data[key] == value
    finally:
        supabase.auth.sign_out()