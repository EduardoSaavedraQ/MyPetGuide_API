import os
from PIL.Image import Image

class ImageSizeLimitExceeded(Exception):
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
    def __init__(self, image: Image | None = None):
        if image is not None:
            self.actual_format: str = image.format
            self.description = f"Formato de imagen no permitido. Formato recibido: {self.actual_format}"
        else:
            self.description = "Formato de imagen no permitido"

    def __str__(self):
        return self.description