import os
import base64
import pytest
from PIL import UnidentifiedImageError
from utils.image_utils import validate_image
from exceptions.image_exceptions import ImageTooLarge, InvalidImageFormat, NoImageFormatFound

# Rutas
JPEG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_compressed.txt")
PNG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_compressed.txt")
JPEG_INVALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_overweigthed.txt")
PNG_INVALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_overweigthed.txt")
GIF_INVALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_gif.txt")
FAKE_IMAGE_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/pdf_con_cabecera_jpg.txt")

@pytest.mark.parametrize(
    ("image_path", "expected_exception", "file_size_limit"),
    [
        (JPEG_VALID_IMAGE_PATH, None, "100"),
        (PNG_VALID_IMAGE_PATH, None, "100"),
        (JPEG_INVALID_IMAGE_PATH, ImageTooLarge, "100"),
        (PNG_INVALID_IMAGE_PATH, ImageTooLarge, "100"),
        (GIF_INVALID_IMAGE_PATH, InvalidImageFormat, "1000"),
        (FAKE_IMAGE_FILE_PATH, UnidentifiedImageError, "100"),
    ],
    ids=[
        "jpeg valido",
        "png valido",
        "jpeg demasiado grande",
        "png demasiado grande",
        "gif con formato invalido",
        "pdf con cabecera falsificada",
    ]
)
def test_validate_image_comportamiento_por_tipo(monkeypatch: pytest.MonkeyPatch, image_path: str, expected_exception: Exception, file_size_limit: str) -> None:
    monkeypatch.setenv("FILE_SIZE_LIMIT", file_size_limit)

    with open(image_path, 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

    if expected_exception is None:
        validate_image(image_bytes)
    else:
        with pytest.raises(expected_exception):
            validate_image(image_bytes)

def test_validate_image_lanza_excepcion_NoImageFormatFound_con_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FILE_SIZE_LIMIT", "1000")

    class FakeImage:
        format = None

    def fake_open(_):
        return FakeImage()

    monkeypatch.setattr("PIL.Image.open", fake_open)

    # No importa qué bytes pasemos, porque fake_open los ignora
    dummy_bytes = b"fake image bytes"

    with pytest.raises(NoImageFormatFound):
        validate_image(dummy_bytes)