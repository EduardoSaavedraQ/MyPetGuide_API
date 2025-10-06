from utils.image_utils import is_valid_image_type
from PIL import Image
import os
import io
import base64
import pytest

JPEG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_compressed.txt")
PNG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_compressed.txt")

GIF_INVALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_gif.txt")


@pytest.mark.parametrize(
    ("image_path", "expected"),
    [
        (JPEG_VALID_IMAGE_PATH, True),
        (PNG_VALID_IMAGE_PATH, True),
        (GIF_INVALID_IMAGE_PATH, False)
    ],
    ids=["jpeg valido", "png valido", "gif invalido"]
)
def test_is_valid_image_type_valida_formatos_permitidos(image_path: str, expected: bool) -> None:
    with open(image_path, 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

    im: Image.Image = Image.open(io.BytesIO(image_bytes))

    assert is_valid_image_type(image=im) == expected