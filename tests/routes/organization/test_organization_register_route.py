from fastapi.testclient import TestClient
import httpx
from main import app
from supabase import Client
from utils.supabase import get_supabase_admin_client
import os
import base64
import json
import pytest
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

ORGANIZATION_REGISTER_URL: str = "/organization/register"
FAKE_EMAIL: str = f"test_org@example.com"
FAKE_PASSWORD: str = "password"
GOOD_FAKE_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_compressed.txt")
OVERWEIGHTED_FAKE_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_overweigthed.txt")
GIF_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_gif.txt")
PDF_FAKE_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64_encoded_images/pdf_con_cabecera_jpg.txt")
FAKE_ORGANIZATION_NAME: str = "Test Organization"

SUPABASE_PROFILE_IMAGES_BUCKET_NAME = "avatars"
SUPABASE_ORGANIZATION_IMAGE_PROFILES_PATH = "public/organizations"

FAKE_FULL_DATA: dict = {
    "email" : FAKE_EMAIL,
    "password" : FAKE_PASSWORD,
    "password_confirm" : FAKE_PASSWORD,
    "organization_name" : FAKE_ORGANIZATION_NAME,
    "admin_first_name" : "Test",
    "admin_last_name" : "Organization",
    "admin_slast_name" : "User",
    "biography" : "This is a test organization used for testing purposes."
}

FAKE_NOT_FULL_DATA: dict = {
    "email" : FAKE_EMAIL,
    "password" : FAKE_PASSWORD,
    "password_confirm" : FAKE_PASSWORD,
    "organization_name" : FAKE_ORGANIZATION_NAME,
    "admin_first_name" : "Test",
    "admin_last_name" : "Organization",
}

FAKE_FULL_DATA_DIFFERENT_PASSWORD = {
    "email" : FAKE_EMAIL,
    "password" : FAKE_PASSWORD,
    "password_confirm" : "different",
    "organization_name" : FAKE_ORGANIZATION_NAME,
    "admin_first_name" : "Test",
    "admin_last_name" : "Organization",
    "admin_slast_name" : "User",
    "biography" : "This is a test organization used for testing purposes."
}

FAKE_FULL_DATA_SHORT_PASSWORD = {
    "email" : FAKE_EMAIL,
    "password" : "short",
    "password_confirm" : "short",
    "organization_name" : FAKE_ORGANIZATION_NAME,
    "admin_first_name" : "Test",
    "admin_last_name" : "Organization",
    "admin_slast_name" : "User",
    "biography" : "This is a test organization used for testing purposes."
}

@pytest.mark.parametrize(
    ("test_data", "image_path", "image_extension", "expected_status_code", "expected_error_message"),
    [
        (FAKE_FULL_DATA, GOOD_FAKE_PROFILE_PHOTO_PATH, "png", 200, None),
        (FAKE_FULL_DATA, None, None, 200, None),
        (FAKE_FULL_DATA, OVERWEIGHTED_FAKE_PROFILE_PHOTO_PATH, "png", 422, "Imagen pesa"),
        (FAKE_FULL_DATA, GIF_PROFILE_PHOTO_PATH, "gif", 422, "Formato de imagen no permitido. Formato recibido: GIF"),
        (FAKE_NOT_FULL_DATA, GOOD_FAKE_PROFILE_PHOTO_PATH, "png", 200, None),
        (FAKE_NOT_FULL_DATA, None, None, 200, None),
        (FAKE_FULL_DATA_DIFFERENT_PASSWORD, GOOD_FAKE_PROFILE_PHOTO_PATH, "png", 422, "Las contraseñas no coinciden"),
        (FAKE_FULL_DATA_SHORT_PASSWORD, GOOD_FAKE_PROFILE_PHOTO_PATH, "png", 422, "String should have at least 8 characters"),
    ]
)
def test_organization_register_devuelve_respuestas_esperadas(
        test_data: dict[str, str],
        image_path: str | None,
        image_extension: str | None,
        expected_status_code: int,
        expected_error_message: str,
        monkeypatch: pytest.MonkeyPatch
) -> None:
    
    profile_image_bytes: bytes | None = None
    response: httpx.Response | None = None

    if image_path == GIF_PROFILE_PHOTO_PATH:
        monkeypatch.setenv("FILE_SIZE_LIMIT", "2000")
    else:
        monkeypatch.setenv("FILE_SIZE_LIMIT", "200")

    try:
        files = {"data": (None, json.dumps(test_data))}

        if image_path:
            with open(image_path, 'r') as f:
                profile_image_bytes = base64.b64decode(f.read())

            files["image"] = (f"profile_photo.{image_extension}", profile_image_bytes, f"image/{image_extension}")

        response = client.post(
            url=ORGANIZATION_REGISTER_URL,
            files=files
        )

        response_data: dict = response.json()

        assert response.status_code == expected_status_code

        if expected_status_code == 200:
            assert "jwt" in response_data and response_data["jwt"] is not None
            assert "id_organization" in response_data and response_data["id_organization"] is not None
            assert "id_user" in response_data and response_data["id_user"] is not None

            for key, value in test_data.items():
                if key not in {"email", "password", "password_confirm"}:
                    assert key in response_data and response_data[key] == value

            if image_path:
                response_data = response.json()

                supabase: Client = get_supabase_admin_client()

                supabase_response: list = (
                    supabase.storage
                    .from_(SUPABASE_PROFILE_IMAGES_BUCKET_NAME)
                    .list(SUPABASE_ORGANIZATION_IMAGE_PROFILES_PATH)
                )

                assert any(item["name"] == response_data["photo_url"].split('/')[-1] for item in supabase_response)

        else:
            assert "detail" in response_data and expected_error_message in response_data["detail"]

    finally:
        if response and response.status_code == 200:
            response_data: dict = response.json()

            supabase: Client = get_supabase_admin_client()

            supabase.auth.admin.delete_user(response_data["id_user"])

            if response_data["photo_url"]:
                supabase.storage.from_(SUPABASE_PROFILE_IMAGES_BUCKET_NAME).remove([response_data["photo_url"]])