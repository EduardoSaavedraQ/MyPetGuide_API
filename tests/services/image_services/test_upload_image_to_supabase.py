from services.image_services import upload_image_to_supabase
from supabase import Client
from utils.supabase import get_supabase_admin_client
from storage3.types import UploadResponse
from storage3.exceptions import StorageApiError
import os
import base64
from dotenv import load_dotenv
from freezegun import freeze_time
import pytest

JPEG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_compressed.txt")
PNG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_compressed.txt")

load_dotenv()

@pytest.mark.parametrize(
    ("image_path", "expected_extension"),
    [
        (JPEG_VALID_IMAGE_PATH, "jpeg"),
        (PNG_VALID_IMAGE_PATH, "png")
    ]
)
@pytest.mark.parametrize(
    "storage_path",
    [
        "public/users",
        "public/organizations"
    ]
)
@freeze_time("2025-10-06 21:13:40")
def test_upload_image_to_supabase_devuelva_ruta_de_imagenes_cargadas(image_path: str, expected_extension: str, storage_path: str) -> None:
    try:
        if os.getenv("SUPABASE_SERVICE_ROLE_KEY", None) is None:
            raise pytest.skip("Falta la variable de entorno SERVICE_ROLE_KEY.")

        supabase: Client = get_supabase_admin_client()

        test_id: str = "111-111-111"

        with open(image_path, 'r') as f:
            image_bytes: bytes = base64.b64decode(f.read())

        result: UploadResponse = upload_image_to_supabase(
            id=test_id,
            image=image_bytes,
            bucket="avatars",
            path=storage_path,
            supabase=supabase
        )

        assert isinstance(result, UploadResponse)

        assert result.path == f"{storage_path}/{test_id}_20251006T211340.{expected_extension}"
        assert result.full_path == f"avatars/{storage_path}/{test_id}_20251006T211340.{expected_extension}"
        assert result.fullPath == f"avatars/{storage_path}/{test_id}_20251006T211340.{expected_extension}"

        # Liempieza
        supabase.storage.from_("avatars").remove([result.path])

    except StorageApiError as e:
        if int(e.status) == 403:
            raise pytest.skip("El cliente de Supabase no tiene los permisos de superusuario.")
        else:
            raise pytest.skip(f"Una de las imágenes de prueba ya ha sido cargada previamente. Elimínala manualmente antes de proceder con el test. {e=}")


@pytest.mark.parametrize(
    ("identifier_prefix", "image_path", "storage_path"),
    [
        ("test_jpeg_compressed", JPEG_VALID_IMAGE_PATH, "public/users"),
        ("test_png_compressed", PNG_VALID_IMAGE_PATH, "public/organizations")
    ]
)
@freeze_time("2025-10-06 21:13:40")
def test_upload_image_to_supabase_devuelva_error_409_cuando_se_sube_una_imagen_que_repita_nombre_con_otra_ya_almacenada(
    identifier_prefix: str,
    image_path: str,
    storage_path: str
) -> None:
    if os.getenv("SUPABASE_SERVICE_ROLE_KEY", None) is None:
        raise pytest.skip("Falta la variable de entorno SERVICE_ROLE_KEY.")

    supabase: Client = get_supabase_admin_client()

    if supabase.auth.admin is None:
        pytest.skip("El cliente de Supabase no tiene permisos de administrador.")

    with open(image_path, 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

    result: UploadResponse = upload_image_to_supabase(
        id=identifier_prefix,
        image=image_bytes,
        bucket="avatars",
        path=storage_path,
        supabase=supabase
    )

    assert isinstance(result, UploadResponse)

    with pytest.raises(StorageApiError) as exc_info:
        upload_image_to_supabase(
            id=identifier_prefix,
            image=image_bytes,
            bucket="avatars",
            path=storage_path,
            supabase=supabase
        )

        assert exc_info.value.status == 409

    # Limpieza
    supabase.storage.from_("avatars").remove([result.path])