from sqlmodel import SQLModel, Field
from pydantic import PositiveInt

class PetCreate(SQLModel):
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