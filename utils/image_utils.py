import os
import io
import PIL
from PIL import Image
from datetime import datetime
from exceptions.image_exceptions import ImageTooLarge, NoImageFormatFound, InvalidImageFormat

def verify_image_size(image: bytes) -> bool:
    """
    Verifica que el peso de la imagen (en kilobytes) sea menor o igual al establecido en la variable de entorno 'FILE_SIZE_LIMIT'.

    Args:
        image (bytes): Bytes de la imagen cuyo tamaño se quiere verificar.

    Returns:
        bool: Resultado de evaluar si el peso/longitud de la imagen es menor o igual al establecido en las variables de entorno.
    """

    return len(image) / 1024 <= int(os.getenv("FILE_SIZE_LIMIT"))

def is_valid_image_type(image: Image.Image) -> bool:
    """
    Determina si el formato de la imagen se encuentra dentro de los aceptados.

    Args:
        image (Image.Image): Objeto de imagen abierto con PIL, que debe contener el atributo `format`.

    Returns:
        bool: Resultado de evaluar si el formato de la imagen se encuentra dentro de los admitidos.

    Raises:
        exceptions.image_exceptions.NoImageFormatFound: Si la imagen no tiene un formato definido.
    """

    valid_image_types = {'PNG', 'JPEG', 'JPG'}

    return image.format in valid_image_types

def validate_image(image: bytes) -> None:
    """
    Agrupa todas las validaciones de una imagen.

    Args:
        image (bytes): Bytes de la imagen que se quiere validar.

    Returns:
        bool: Resultado que indica si la imagen pasó o no todas las validaciones.

    Raises:
        PIL.UnidentifiedImageError: Si los bytes no representan una imagen válida.
        ImageTooLarge: Si el tamaño de la imagen excede el límite permitido.
        NoImageFormatFound: Si la imagen no tiene un formato definido.
        InvalidImageFormat: Si el formato de la imagen no está entre los aceptados.

    """

    if not verify_image_size(image):
        raise ImageTooLarge(image)

    im = PIL.Image.open(io.BytesIO(image))

    if not im.format:
        raise NoImageFormatFound

    if not is_valid_image_type(im):
        raise InvalidImageFormat(im)

def generate_image_filename(id: str, image: Image.Image) -> str:
    """
    Genera el nombre de archivo de la imagen recibida. Se recomienda usar después de haber validado la imagen.

    Args:
        id (str): El ID del propietario de la imagen.
        image (Image.Image): Objeto de imagen abierto con PIL, que debe contener el atributo `format`.

    Returns:
        str: El nombre del archivo en el formato <id_propietario>_<timestamp>.<ext>
    """
    timestamp: str = datetime.now().strftime("%Y%m%dT%H%M%S")
    extension: str = image.format.lower()

    return f"{id}_{timestamp}.{extension}"