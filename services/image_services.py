from supabase import Client
from storage3.types import UploadResponse
from PIL import Image
from utils.image_utils import generate_image_filename
import io

def upload_image_to_supabase(id: str, image: bytes, bucket: str, path: str, supabase: Client) -> UploadResponse:
    """
    Carga una imagen al bucket especificado en Supabase. Se recomienda realizar validaciones antes de utilizar este servicio.

    Args:
        id (str): ID del propietario de la imagen.
        image (bytes): bytes de la imagen que se va a cargar en supabase.
        bucket (str): nombre del bucket en el que se va a cargar la imagen.
        path (str): ruta (sin nombre de archivo) en la que se va a almacenar la imagen.
        supabase (supabase.Client): Cliente de Supabase que se usará para cargar la imagen.

    Returns:
        storage3.types.UploadResponse: Un objeto que contiene el nombre y la ruta completa de la imagen cargada.

    Raises:
        storage3.types.StorageApiError: Si ocurre un error al subir la imagen, generalemente por duplicados o permisos insuficientes.
    """
    im = Image.open(io.BytesIO(image))   

    image_filename: str = generate_image_filename(id=id, image=im)
    content_type: str = f"image/{im.format.lower()}"

    response = (
        supabase.storage
        .from_(bucket)
        .upload(
            file=image,
            path=f"{path}/{image_filename}",
            file_options={
                "upsert": "true",
                "content-type": content_type
            }
        )
    )

    return response