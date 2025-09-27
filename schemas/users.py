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
    id_profile: int
    id_user: UUID
    first_name: str
    last_name: str
    slast_name: str | None = None
    photo_url: str | None = None
    house_size: str | None = None
    house_backyard_size: str | None = None
    family_size: str | None = None
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
    house_size: str | None = None
    house_backyard_size: str | None = None
    family_size: str | None = None
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