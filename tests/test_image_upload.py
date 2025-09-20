from utils.image_utils import verify_image_size, is_valid_image_type
from supabase import Client
from utils.supabase import get_supabase_client
from utils.image_utils import generate_image_filename
from dotenv import load_dotenv
import base64
from PIL import Image, UnidentifiedImageError
import io
import pytest
from services.image_service import upload_image_to_supabase

load_dotenv()

def test_detectar_si_imagen_supera_el_limite_maximo() -> None:
    image_overweighted_passes: bool = False
    image_compressed_passes: bool = False

    with open("tests/b64encoded_images/test_jpeg_overweigthed.txt", "r") as f:
        image_bytes: bytes = base64.b64decode(f.read())

        image_overweighted_passes = verify_image_size(image_bytes)

    with open("tests/b64encoded_images/test_jpeg_compressed.txt", "r") as f:
        image_bytes: bytes = base64.b64decode(f.read())

        image_compressed_passes = verify_image_size(image_bytes)

    assert not image_overweighted_passes
    assert image_compressed_passes

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

def test_validar_formato_de_imagen() -> None:
    with open('tests/b64encoded_images/test_jpeg_compressed.txt', 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

        im = Image.open(io.BytesIO(image_bytes))

        assert is_valid_image_type(im)

    with open('tests/b64encoded_images/test_png_compressed.txt', 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

        im = Image.open(io.BytesIO(image_bytes))

        assert is_valid_image_type(im)

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

def test_subir_imagen_de_perfil_de_usuario_a_supabase() -> None:
    with open("tests/b64encoded_images/test_jpeg_compressed.txt", "r") as f:
        image_bytes: bytes = base64.b64decode(f.read())
        im = Image.open(io.BytesIO(image_bytes))
        username: str = "user_test"
        filename: str = generate_image_filename(id=username, image=im)

        try:
            supabase: Client = get_supabase_client(admin=True)

            response = upload_image_to_supabase(
                id=username,
                image=image_bytes,
                bucket="avatars",
                path="public/users",
                supabase=supabase
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
        
        except Exception as e:
            pytest.fail(f"Ha ocurrido un error inesperado: {e=}")
        finally:
            supabase.storage.empty_bucket("avatars")

def test_subir_imagen_de_perfil_de_organizacion_a_supabase() -> None:
    with open("tests/b64encoded_images/test_png_compressed.txt", 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())
        im = Image.open(io.BytesIO(image_bytes))
        organization_name: str = "test_organization"
        filename: str = generate_image_filename(id=organization_name, image=im)

        try:

            supabase: Client = get_supabase_client(admin=True)

            response = upload_image_to_supabase(
                id=organization_name,
                image=image_bytes,
                bucket="avatars",
                path="public/organizations",
                supabase=supabase
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
        
        except Exception as e:
            pytest.fail(f"Ha ocurrido un error inesperado: {e=}")

        finally:
            supabase.storage.empty_bucket("avatars")

def test_subir_imagen_de_perfil_de_usuario_cuando_tiene_un_formato_no_valido() -> None:
    from exceptions.image_exceptions import InvalidImageFormat

    with open("tests/b64encoded_images/test_gif.txt", 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())
        username: str = "user_test"

        try:

            supabase: Client = get_supabase_client(admin=True)

            response = upload_image_to_supabase(
                id=username,
                image=image_bytes,
                bucket="avatars",
                path="public/users",
                supabase=supabase
            )

            pytest.fail("Se debería haberse lanzado una excepción")

        except InvalidImageFormat:
            assert True

        except Exception as e:
            pytest.fail(f"Se ha lanzado una excepción no esperada: {e=}")

        finally:
            supabase.storage.empty_bucket("avatars")

def test_subir_imagen_de_perfil_de_usuario_cuando_supera_el_tamanio_maximo() -> None:
    from exceptions.image_exceptions import ImageSizeLimitExceeded

    with open("tests/b64encoded_images/test_jpeg_overweigthed.txt", 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())
        username: str = "user_test"

        try:

            supabase: Client = get_supabase_client(admin=True)

            response = upload_image_to_supabase(
                id=username,
                image=image_bytes,
                bucket="avatars",
                path="public/users",
                supabase=supabase
            )

            pytest.fail("Se debería haberse lanzado una excepción")

        except ImageSizeLimitExceeded:
            assert True

        except Exception as e:
            pytest.fail(f"Se ha lanzado una excepción no esperada: {e=}")

        finally:
            supabase.storage.empty_bucket("avatars")


def test_subir_imagen_de_perfil_de_usuario_valida_pero_sin_permisos_de_administrador() -> None:
    with open("tests/b64encoded_images/test_jpeg_compressed.txt", 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())
        username: str = "user_test"

        try:

            supabase: Client = get_supabase_client(admin=False)

            response = upload_image_to_supabase(
                id=username,
                image=image_bytes,
                bucket="avatars",
                path="public/users",
                supabase=supabase
            )

            pytest.fail("Se debería haberse lanzado una excepción")

        except Exception as e:
            assert True
            print(e)

        finally:
            supabase = get_supabase_client(admin=True)
            supabase.storage.empty_bucket("avatars")