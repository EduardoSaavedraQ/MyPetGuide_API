from sqlmodel import SQLModel, Field
from pydantic import PositiveInt, model_validator
from pydantic_core import PydanticCustomError
from schemas.breed import BreedRead

class PetCreate(SQLModel):
    """Modelo para validar los datos al registrar una nueva mascota.

    Esta clase define todos los campos necesarios para crear un nuevo registro de
    mascota en el sistema. Incluye desde información básica como nombre y raza, hasta
    detalles médicos y de comportamiento. Se utiliza para validar los datos de entrada
    en el endpoint de creación.

    Attributes:
        id_breed1 (PositiveInt): ID de la raza principal de la mascota.
        id_breed2 (PositiveInt | None): ID de la raza secundaria (opcional, para mestizos).
        pet_name (str): Nombre de la mascota.
        sex (bool | None): Sexo de la mascota (True para macho, False para hembra).
        age (PositiveInt | None): Edad de la mascota en años.
        birth_date (str | None): Fecha de nacimiento en formato AAAA-MM-DD.
        pet_description (str | None): Descripción general de la mascota.
        in_adoption_process (bool): Indica si la mascota está actualmente en proceso de adopción.
        vaccinated (bool | None): Indica si está vacunada.
        dewormed (bool | None): Indica si está desparasitada.
        sterilized (bool | None): Indica si está esterilizada.
        has_disabilities (bool | None): Indica si tiene alguna discapacidad.
        sociability (int | None): Nivel de sociabilidad (1-3).
        fur_length (int | None): Longitud del pelaje (0-3).
        shedding_level (int | None): Nivel de muda de pelo (0-3).
        energy_level (int | None): Nivel de energía (1-3).
        care_level_cost (PositiveInt | None): Nivel de costo de cuidado (1-3).
        care_difficulty (PositiveInt | None): Nivel de dificultad de cuidado (1-3).
        pet_size (PositiveInt | None): Tamaño de la mascota (1-4).
        species (bool): Especie (True para perro, False para gato).

    Raises:
        PydanticCustomError: Se lanza si `id_breed1` y `id_breed2` son idénticos.
    """

    id_breed1: PositiveInt = Field(..., description="ID de la raza principal de la mascota")
    id_breed2: PositiveInt | None = Field(default=None, description="ID de la raza secundaria de la mascota (opcional)")
    pet_name: str = Field(..., min_length=1, max_length=50, description="Nombre de la mascota")
    sex: bool | None = Field(default=None, description="Sexo de la mascota (True para macho, False para hembra)")
    age: PositiveInt | None = Field(default=None, description="Edad de la mascota en años")
    birth_date: str | None = Field(default=None, description="Fecha de nacimiento de la mascota en formato AAAA-MM-DD")
    pet_description: str | None = Field(default=None, min_length=1, max_length=500, description="Descripción de la mascota (máximo 500 caracteres)")
    in_adoption_process: bool = Field(default=False, description="Indica si la mascota está en proceso de adopción")
    vaccinated: bool | None = Field(default=None, description="Indica si la mascota está vacunada")
    dewormed: bool | None = Field(default=None, description="Indica si la mascota está desparasitada")
    sterilized: bool | None = Field(default=None, description="Indica si la mascota está esterilizada")
    has_disabilities: bool | None = Field(default=None, description="Indica si la mascota tiene alguna discapacidad")
    sociability: int | None = Field(default=None, ge=0, le=3, description="Nivel de sociabilidad de la mascota (1 a 3)")
    fur_length : int | None = Field(default=None, ge=0, le=3, description="Longitud del pelaje de la mascota (0 a 3)")
    shedding_level: int | None = Field(default=None, ge=0, le=3, description="Nivel de muda de pelaje de la mascota (0 a 3)")
    energy_level: int | None = Field(default=None, ge=0, le=3, description="Nivel de energía de la mascota (1 a 3)")
    care_level_cost: PositiveInt | None = Field(default=None, ge=1, le=3, description="Nivel de costo de cuidado de la mascota (1 a 3)")
    care_difficulty: PositiveInt | None = Field(default=None, ge=1, le=3, description="Nivel de dificultad de cuidado de la mascota (1 a 3)")
    pet_size: PositiveInt | None = Field(default=None, ge=1, le=4, description="Tamaño de la mascota (1 a 3)")
    species: bool = Field(..., description="Especie de la mascota (True para perro, False para gato)")

    @model_validator(mode="after")
    def check_id_breeds_are_different(self) -> "PetCreate":
        """Valida que los IDs de la razas de la mascota no sean el mismo"""
        if self.id_breed1 == self.id_breed2:
            raise PydanticCustomError(
                "same_breed_identifier",
                "Los identificadores de las razas no pueden ser exactamente el mismo"
            )

class PetRead(SQLModel):
    """Representa el perfil público y detallado de una mascota.

    Este modelo se utiliza como respuesta de la API para mostrar la información
    completa de una mascota. A diferencia de `PetCreate`, en lugar de IDs de razas,
    incluye los objetos completos anidados (`BreedRead`) para la raza principal
    y secundaria.

    Attributes:
        id_pet (PositiveInt): El identificador único de la mascota.
        photo_url (str | None): URL de la foto de perfil de la mascota.
        id_owner (str | None): ID del usuario dueño de la mascota (si aplica).
        main_breed (BreedRead): Objeto anidado con la información de la raza principal.
        secondary_breed (BreedRead | None): Objeto anidado para la raza secundaria.
        pet_name (str): Nombre de la mascota.
        sex (bool | None): Sexo de la mascota (True para macho, False para hembra).
        age (int | None): Edad de la mascota en años.
        birth_date (str | None): Fecha de nacimiento en formato AAAA-MM-DD.
        pet_description (str | None): Descripción general de la mascota.
        in_adoption_process (bool): Indica si la mascota está actualmente en proceso de adopción.
        vaccinated (bool | None): Indica si está vacunada.
        dewormed (bool | None): Indica si está desparasitada.
        sterilized (bool | None): Indica si está esterilizada.
        has_disabilities (bool | None): Indica si tiene alguna discapacidad.
        sociability (int | None): Nivel de sociabilidad (1-3).
        fur_length (int | None): Longitud del pelaje (0-3).
        shedding_level (int | None): Nivel de muda de pelo (0-3).
        energy_level (int | None): Nivel de energía (1-3).
        care_level_cost (PositiveInt | None): Nivel de costo de cuidado (1-3).
        care_difficulty (PositiveInt | None): Nivel de dificultad de cuidado (1-3).
        pet_size (PositiveInt | None): Tamaño de la mascota (1-4).
        species (bool): Especie (True para perro, False para gato).
    """

    id_pet: PositiveInt
    photo_url: str | dict | None = None
    id_owner: str | None
    id_breed1: int
    id_breed2: int | None = None
    main_breed: BreedRead
    secondary_breed: BreedRead | None = None
    pet_name: str | None = None
    sex: bool | None = None
    age: int | None = None
    birth_date: str | None = None
    pet_description: str | None = None
    in_adoption_process: bool = False
    vaccinated: bool | None = None
    dewormed: bool | None = None
    sterilized: bool | None = None
    has_disabilities: bool | None = None
    sociability: int | None = None
    fur_length: int | None = None
    shedding_level: int | None= None
    energy_level: int | None = None
    care_level_cost: PositiveInt | None = None
    care_difficulty: PositiveInt | None = None
    pet_size: PositiveInt | None = None

class PetReadWithPetLabel(PetRead):
    """Extensión de `PetRead` que incluye una etiqueta de clasificación.

    Hereda todos los campos de `PetRead` y añade el campo `pet_label`, que
    representa el clúster al que pertenece la mascota en el sistema de recomendación).

    Attributes:
        pet_label (int | None): Etiqueta de clasificación o clúster de la mascota.

    Los demás atributos son heredados de `PetRead`.
    """

    pet_label: int | None = None

class CompatiblePetClusters(SQLModel):
    """
    Modelo de respuesta para la predicción de grupos compatibles entre un usuario y mascotas.

    Attributes:
        pet_clusters (list[int]): Lista de identificadores de cluster o etiquetas de grupos compatibles.
        probabilities (list[float]): Lista de probabilidades o puntuaciones asociadas a cada elemento en `pet_clusters`.
        clusters_descriptions (list[str]): Lista con el resumen de los clústeres asociados a cada elemento en `pet_clusters`.
        clusters_titles (list[str]): Lista de los títulos de los clústeres asociados a cada elemento en `pet_clusters`.
    """

    pet_clusters: list[int]
    probabilities: list[float]
    clusters_descriptions: list[str]
    clusters_titles: list[str]

class PetChatInfo(SQLModel):
    id_pet: int
    pet_name: str
    photo_url: str | None = None