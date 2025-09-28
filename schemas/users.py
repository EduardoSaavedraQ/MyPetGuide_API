from sqlmodel import SQLModel, Field
from pydantic import EmailStr, model_validator
from pydantic_core import PydanticCustomError
from uuid import UUID

class UserCreate(SQLModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, max_length=16, description="Contraseña del usuario (8-16 caracteres)")
    password_confirm: str
    first_name: str = Field(..., min_length=1, max_length=50, description="Nombre(s) del usuario")
    last_name: str = Field(..., min_length=1, max_length=50, description="Apellido paterno del usuario")
    slast_name: str | None = Field(default=None, min_length=1, max_length=50, description="Apellido materno del usuario (opcional)")

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise PydanticCustomError(
                'passwords_mismatch',  # Un código de error único que tú inventas
                'Las contraseñas no coinciden'  # El mensaje exacto que quieres mostrar
            )
        
        return self

class UserRead(SQLModel):
    id_profile: int | None = None
    id_user: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    slast_name: str | None = None
    photo_url: str | None = None
    house_size: int | None = None
    house_backyard_size: int | None = None
    family_size: int | None = None
    has_kids: bool | None = None
    has_neighbors: bool | None = None
    available_time_per_day: int | None = None
    vet_access: bool | None = None
    has_other_pets: bool | None = None
    experience_with_pets: int | None = None
    preferred_species: bool | None = None

class UserCreated(SQLModel):
    jwt: str | None = None
    id_profile: int
    id_user: UUID
    first_name: str
    last_name: str
    slast_name: str | None = None
    photo_url: str | None = None
    house_size: int | None = None
    house_backyard_size: int | None = None
    family_size: int | None = None
    has_kids: bool | None = None
    has_neighbors: bool | None = None
    available_time_per_day: int | None = None
    vet_access: bool | None = None
    has_other_pets: bool | None = None
    experience_with_pets: int | None = None
    preferred_species: bool | None = None

    def get_full_name(self) -> str:
        fullname: str = f"{self.first_name} {self.last_name}"
        if self.slast_name:
            fullname += f" {self.slast_name}"
        return fullname

class UserProfileCreate(SQLModel):
    house_size: int | None = Field(default=None, ge=40, description="Tamaño de la casa en metros cuadrados (mínimo 40 m²)")
    house_backyard_size: int | None = Field(default=None, ge=0, description="Tamaño del patio trasero/cochera/terraza en metros cuadrados (mínimo 0 m²)")
    family_size: int | None = Field(default=None, ge=1)
    has_kids: bool | None = Field(default=None, description="Indica si hay niños en la familia")
    has_neighbors: bool | None = Field(default=None, description="Indica si hay vecinos cerca")
    available_time_per_day: int | None = Field(default=None, gt=0, le=24, description="Tiempo disponible al día para cuidar a la mascota (en horas, máximo 24)")
    vet_access: bool | None = Field(default=None, description="Indica si se tiene acceso a un veterinario")
    has_other_pets: bool | None = Field(default=None, description="Indica si ya se tienen otras mascotas")
    experience_with_pets: int | None = Field(default=None, description="Tiempo experiencia cuidando mascotas")
    preferred_species: bool | None = Field(default=None, description="Preferencia por especie de mascota (True para perro, False para gato)")