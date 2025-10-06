import os
import pytest
from pytest import MonkeyPatch
from utils.image_utils import verify_image_size
import base64

JPEG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_compressed.txt")
PNG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_compressed.txt")

JPEG_INVALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_overweigthed.txt")
PNG_INVALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_overweigthed.txt")

@pytest.mark.parametrize(
    ("image_path", "expected"),
    [
        (JPEG_VALID_IMAGE_PATH, True),
        (PNG_VALID_IMAGE_PATH, True),
        (JPEG_INVALID_IMAGE_PATH, False),
        (PNG_INVALID_IMAGE_PATH, False)
    ],
    ids=["jpeg valido", "png valido", "jpeg invalido", "png invalido"]
)
def test_verify_image_size_valida_imagenes_por_debajo_del_limite_permitido(image_path: str, expected: bool, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(name="FILE_SIZE_LIMIT", value="100")

    with open(image_path, 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

    assert verify_image_size(image_bytes) == expected