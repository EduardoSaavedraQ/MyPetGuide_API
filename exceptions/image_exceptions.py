import os
from PIL import Image

class ImageTooLarge(Exception):
    """
    Excepción lanzada cuando el tamaño de la imagen excede el límite permitido.

    :param image: Bytes de la imagen. Si se proporciona, se calcula el tamaño real en KB
    y se incluye en el mensaje de error. Si no se proporciona, se usa un mensaje genérico.
    :type image: bytes | None

    Attributes:
        actual_size (float): Tamaño real de la imagen en KB (si se proporciona).
        size_limit (float): Límite de tamaño permitido en KB, obtenido de la variable de entorno FILE_SIZE_LIMIT.
        description (str): Mensaje descriptivo del error.

    Example:
        raise ImageTooLarge(image_bytes)
    """


    def __init__(self, image: bytes | None = None):
        if image is not None:
            self.actual_size: float = len(image) / 1024
            self.size_limit: float = os.getenv("FILE_SIZE_LIMIT")
            self.description: str = f"Imagen pesa {self.actual_size:2f} KB. El límite es de {self.size_limit} KB"
        else:
            self.description: str = "La imagen excede el tamaño permitido."

    def __str__(self):
        return self.description

class InvalidImageFormat(Exception):
    """
    Excepción lanzada cuando el formato de la imagen no está entre los formatos válidos permitidos.

    :param image: Objeto PIL de la imagen. Si se proporciona, se extrae el atributo `.format`
    para incluirlo en el mensaje de error. Si no se proporciona, se usa un mensaje genérico.
    :type image: PIL.Image.Image | None

    Attributes:
        actual_format (str): Formato detectado de la imagen (si se proporciona).
        description (str): Mensaje descriptivo del error.

    Example:
        raise InvalidImageFormat(im)
    """

    def __init__(self, image: Image.Image | None = None):
        if image is not None:
            self.actual_format: str = image.format
            self.description = f"Formato de imagen no permitido. Formato recibido: {self.actual_format}"
        else:
            self.description = "Formato de imagen no permitido"

    def __str__(self):
        return self.description

class NoImageFormatFound(Exception):
    """
    Excepción lanzada cuando la imagen no tiene un formato definido.

    Esta excepción se utiliza cuando el atributo `.format` del objeto PIL es `None`,
    lo que indica que no se pudo determinar el tipo de imagen.

    Attributes:
        description (str): Mensaje descriptivo del error.

    Example:
        raise NoImageFormatFound()
    """

    def __init__(self):
        self.description = "La imagen no tiene formato definido."
        
    def __str__(self):
        return self.description