from sqlmodel import SQLModel
from pydantic import PositiveInt

class BreedRead(SQLModel):
    """Representa los datos de una raza de animal.

    Este modelo se utiliza para devolver la información esencial de una raza 
    de animal desde la base de datos, como su nombre y la especie a la que 
    pertenece (perro o gato).

    Attributes:
        id_breed (PositiveInt): El identificador único de la raza.
        breed_name (str): El nombre común de la raza (ej. "Labrador", "Siamese").
        species (bool): La especie a la que pertenece la raza 
                        (convencionalmente: True para perro, False para gato).
    """

    id_breed: PositiveInt
    breed_name: str
    species: bool