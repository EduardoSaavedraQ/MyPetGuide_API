from fastapi.testclient import TestClient
import httpx
from main import app
from supabase import Client
from supabase_auth import AuthResponse
from utils.supabase import get_supabase_admin_client
import os
import base64
import json
import pytest
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

PET_REGISTER_URL: str = "/pet/register"
EMAIL_PREREGISTERED_ORGANIZATION_ACCOUNT: str = "organizationtest@gmail.com"
ID_PREREGISTERED_ORGANIZATION_ACCOUNT: str = "121c7d78-798d-46fe-b0ee-392c0853d11e"
GOOD_FAKE_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_compressed.txt")
OVERWEIGHTED_FAKE_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_overweigthed.txt")
GIF_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_gif.txt")
PDF_FAKE_PROFILE_PHOTO_PATH: str = os.path.join(os.path.dirname(__file__), "../../b64_encoded_images/pdf_con_cabecera_jpg.txt")

SUPABASE_PROFILE_IMAGES_BUCKET_NAME = "avatars"
SUPABASE_PET_IMAGE_PROFILES_PATH = "public/pets"

FAKE_FULL_DATA_DOG: dict = {
    "id_breed1": 52,
    "id_breed2": None,
    "pet_name": "Firulais",
    "sex": True,
    "age": 5,
    "birth_date": "2020-06-30",
    "pet_description": "Es muy juguetón.",
    "in_adoption_process": True,
    "vaccinated": False,
    "dewormed": True,
    "sterilized": True,
    "has_disabilities": False,
    "sociability": 2,
    "fur_length": 3,
    "shedding_level": 2,
    "energy_level": 2,
    "care_level_cost": 1,
    "care_difficulty": 3,
    "pet_size": 3,
    "species": True
}

@pytest.mark.parametrize(
    ("test_data", "image_path", "image_extension", "expected_status_code", "expected_error_message", "pet_owner_email", "pet_owner_password", "pet_owner_id", "expects_label"),
    [
        (FAKE_FULL_DATA_DOG, GOOD_FAKE_PROFILE_PHOTO_PATH, "png", 200, None, EMAIL_PREREGISTERED_ORGANIZATION_ACCOUNT, "password", ID_PREREGISTERED_ORGANIZATION_ACCOUNT, True),
        (FAKE_FULL_DATA_DOG, None, None, 200, None, EMAIL_PREREGISTERED_ORGANIZATION_ACCOUNT, "password", ID_PREREGISTERED_ORGANIZATION_ACCOUNT, True),
        (FAKE_FULL_DATA_DOG, OVERWEIGHTED_FAKE_PROFILE_PHOTO_PATH, "png", 422, "Imagen pesa", EMAIL_PREREGISTERED_ORGANIZATION_ACCOUNT, "password", ID_PREREGISTERED_ORGANIZATION_ACCOUNT, True),
        (FAKE_FULL_DATA_DOG, GIF_PROFILE_PHOTO_PATH, "gif", 422, "Formato de imagen no permitido. Formato recibido: GIF", EMAIL_PREREGISTERED_ORGANIZATION_ACCOUNT, "password", ID_PREREGISTERED_ORGANIZATION_ACCOUNT, True),
    ]
)
def test_user_register_devuelve_respuestas_esperadas(
        test_data: dict[str, str],
        image_path: str | None,
        image_extension: str | None,
        expected_status_code: int,
        expected_error_message: str,
        pet_owner_email: str,
        pet_owner_password: str,
        pet_owner_id: str,
        expects_label: bool,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    
    profile_image_bytes: bytes | None = None
    response: httpx.Response | None = None

    supabase: Client = get_supabase_admin_client()

    login_response: AuthResponse = supabase.auth.sign_in_with_password({
        "email": pet_owner_email,
        "password": pet_owner_password
    })

    if not login_response.session:
        raise pytest.skip(f"El usuario con email {pet_owner_email} no existe o la contraseña usada no es correcta.")

    access_token: str = login_response.session.access_token

    if image_path == GIF_PROFILE_PHOTO_PATH:
        monkeypatch.setenv("FILE_SIZE_LIMIT", "2000")
    else:
        monkeypatch.setenv("FILE_SIZE_LIMIT", "100")

    try:
        files = {"data": (None, json.dumps(test_data))}

        if image_path:
            with open(image_path, 'r') as f:
                profile_image_bytes = base64.b64decode(f.read())

            files["image"] = (f"profile_photo.{image_extension}", profile_image_bytes, f"image/{image_extension}")

        response = client.post(
            url=PET_REGISTER_URL,
            files=files,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        response_data: dict = response.json()

        if response.status_code != expected_status_code: print(json.dumps(response_data, indent=4))

        assert response.status_code == expected_status_code

        if expected_status_code == 200:
            assert response_data["id_pet"] is not None
            assert response_data["id_owner"] == pet_owner_id
            assert response_data["main_breed"] is not None and "breed_name" in response_data["main_breed"] and "species" in response_data["main_breed"]

            if test_data["id_breed2"]:
                assert response_data["secondary_breed"] is not None and "breed_name" in response_data["secondary_breed"] and "species" in response_data["secondary_breed"]

            if expects_label:
                assert response_data["pet_label"] is not None

            for key, value in test_data.items():
                if key not in {"id_breed1", "id_breed2", "species"}:
                    assert key in response_data and response_data[key] == value

            if image_path:
                response_data = response.json()

                supabase: Client = get_supabase_admin_client()

                supabase_response: list = (
                    supabase.storage
                    .from_(SUPABASE_PROFILE_IMAGES_BUCKET_NAME)
                    .list(SUPABASE_PET_IMAGE_PROFILES_PATH)
                )

                assert any(response_data["id_owner"] in item["name"] == response_data["photo_url"].split('/')[-1] for item in supabase_response)

        else:
            assert "detail" in response_data and expected_error_message in response_data["detail"]

    finally:
        if response and response.status_code == 200:
            response_data: dict = response.json()

            supabase: Client = get_supabase_admin_client()

            response = (
                supabase.table("pets")
                .delete()
                .eq("id_pet", response_data["id_pet"])
                .execute()
            )

            if response_data["photo_url"]:
                supabase.storage.from_(SUPABASE_PROFILE_IMAGES_BUCKET_NAME).remove([response_data["photo_url"]])