import os
from PIL.Image import Image
from datetime import date

def verify_image_size(image: bytes) -> bool:
    return len(image) / 1024 < int(os.getenv("FILE_SIZE_LIMIT"))

def is_valid_image_type(image: Image) -> bool:
    valid_image_types = {'PNG', 'JPEG', 'JPG'}

    return image.format in valid_image_types

def generate_image_filename(id: str, image: Image) -> str:
    return f"{id}_{date.today()}.{image.format.lower()}"