from utils.image_utils import generate_image_filename
from PIL import Image
import os
import io
import base64
from freezegun import freeze_time
import pytest

JPEG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_jpeg_compressed.txt")
PNG_VALID_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "../../b64encoded_images/test_png_compressed.txt")

@pytest.mark.parametrize(
    ("image_path", "expected_extension"),
    [
        (JPEG_VALID_IMAGE_PATH, "jpeg"),
        (PNG_VALID_IMAGE_PATH, "png")
    ]
)
@freeze_time("2025-10-06 21:13:40")
def test_generate_image_filename_genera_nombres_con_la_fecha_del_sistema(image_path: str, expected_extension: str) -> None:
    test_id: str = "111-111-111"

    with open(image_path, 'r') as f:
        image_bytes: bytes = base64.b64decode(f.read())

    im: Image.Image = Image.open(io.BytesIO(image_bytes))

    expected_filename: str = f"{test_id}_20251006T211340.{expected_extension}"

    assert generate_image_filename(id=test_id, image=im) == expected_filename