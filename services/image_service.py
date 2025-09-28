from supabase import Client
from storage3.types import UploadResponse
import PIL.Image
from utils.image_utils import *
from exceptions.image_exceptions import ImageSizeLimitExceeded, InvalidImageFormat
import io

def upload_image_to_supabase(id: str, image: bytes, bucket: str, path: str, supabase: Client) -> UploadResponse:
    im = PIL.Image.open(io.BytesIO(image))    

    if not is_valid_image_type(im):
        raise InvalidImageFormat

    if not verify_image_size(image):
        raise ImageSizeLimitExceeded(image)

    image_filename: str = generate_image_filename(id=id, image=im)

    response = (
        supabase.storage
        .from_(bucket)
        .upload(
            file=image,
            path=f"{path}/{image_filename}",
            file_options={
                "upsert": "true",
                "content-type": f"image/{im.format.lower()}"
            }
        )
    )

    return response

def replace_image_profile(id: str, image: bytes, bucket: str, path: str, supabase: Client) -> UploadResponse:
    im = PIL.Image.open(io.BytesIO(image))    

    if not is_valid_image_type(im):
        raise InvalidImageFormat

    if not verify_image_size(image):
        raise ImageSizeLimitExceeded(image)

    image_filename: str = generate_image_filename(id=id, image=im)

    response = (
        supabase.storage
        .from_(bucket)
        .upload(
            file=image,
            path=f"{path}/{image_filename}",
            file_options={
                "upsert": "true",
                "content-type": f"image/{im.format.lower()}"
            }
        )
    )

    return response