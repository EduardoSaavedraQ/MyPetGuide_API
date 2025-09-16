from supabase import Client
from utils.supabase import get_supabase_client
from dotenv import load_dotenv
import base64
from PIL import Image, UnidentifiedImageError
import io
import pytest
from datetime import date
import os

load_dotenv()
FILE_SIZE_LIMIT: int = int(os.getenv("FILE_SIZE_LIMIT"))

def test_detectar_si_imagen_supera_el_limite_maximo() -> None:
    image_overweighted = True
    image_compressed = True

    with open("tests/b64encoded_images/test_jpeg_overweigthed.txt", "r") as f:
        image_bytes: bytes = base64.b64decode(f.read())

        if len(image_bytes) / 1024 > FILE_SIZE_LIMIT:
            image_overweighted = False

    with open("tests/b64encoded_images/test_jpeg_compressed.txt", "r") as f:
        image_bytes: bytes = base64.b64decode(f.read())

        if len(image_bytes) / 1024 > FILE_SIZE_LIMIT:
            image_compressed = False

    assert not image_overweighted
    assert image_compressed

def test_comprobar_que_la_imagen_sea_jpg() -> None:
    with open('tests/b64encoded_images/test_jpeg_compressed.txt', 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

        im = Image.open(io.BytesIO(image_bytes))

        assert im.format == 'JPEG'

def test_comprobar_que_la_imagen_sea_png() -> None:
    with open('tests/b64encoded_images/test_png_compressed.txt', 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

        im = Image.open(io.BytesIO(image_bytes))

        assert im.format == 'PNG'

def test_detectar_archivo_con_cabecera_falsificada_para_pasar_por_imagen() -> None:
    with open("tests/b64encoded_images/pdf_con_cabecera_jpg.txt", 'r') as f:
        try:
            image_bytes: bytes = base64.b64decode(f.read())

            im = Image.open(io.BytesIO(image_bytes))

            pytest.fail("Se debió lanzar una excepción si el archivo no era válido")
        
        except UnidentifiedImageError:
            assert True
        
        except Exception as exception:
            pytest.fail(f"Se ha lanzado otro tipo de excepción: {exception=}")

def test_subir_imagen_de_perfil_de_usuario_a_supabase():
    with open("tests/b64encoded_images/test_jpeg_compressed.txt", "r") as f:
        image_bytes: bytes = base64.b64decode(f.read())
        im = Image.open(io.BytesIO(image_bytes))
        extension: str = im.format.lower()
        username: str = "user_test"
        filename: str = f"{username}_{date.today()}.{extension}"

        supabase: Client = get_supabase_client(admin=True)

        response = (
            supabase.storage
            .from_("avatars")
            .upload(
                file=image_bytes,
                path=f'public/users/{filename}',
                file_options={
                    "upsert": "true",
                    "content-type": f"image/{extension}"
                }
            )
        )

        assert response.path == f'public/users/{filename}'
        assert response.full_path == f'avatars/public/users/{filename}'

        response = (
            supabase.storage
            .from_("avatars")
            .list(
                path="public/users"
            )
        )

        assert any(item['name'] == filename for item in response)

        (
            supabase.storage
            .from_('avatars')
            .remove([f'public/users/{filename}'])
        )

def test_subir_imagen_de_perfil_de_organizacion_a_supabase():
    with open("tests/b64encoded_images/test_png_compressed.txt", 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())
        im = Image.open(io.BytesIO(image_bytes))
        extension: str = im.format.lower()
        organization_name: str = "test_organization"
        filename: str = f"{organization_name}_{date.today()}.{extension}"

        supabase: Client = get_supabase_client(admin=True)

        response = (
            supabase.storage
            .from_("avatars")
            .upload(
                file=image_bytes,
                path=f"public/organizations/{filename}",
                file_options={
                    "upsert": "true",
                    "content-type": f"image/{extension}"
                }
            )
        )

        assert response.path == f'public/organizations/{filename}'
        assert response.full_path == f'avatars/public/organizations/{filename}'

        response = (
            supabase.storage
            .from_("avatars")
            .list(
                path="public/organizations"
            )
        )

        assert any(item['name'] == filename for item in response)

        (
            supabase.storage
            .from_('avatars')
            .remove([f'public/organizations/{filename}'])
        )