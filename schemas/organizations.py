from sqlmodel import SQLModel, Field
from uuid import UUID
from pydantic import EmailStr, model_validator
from pydantic_core import PydanticCustomError

class OrganizationCreate(SQLModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, max_length=16, description="Contraseña del usuario (8-16 caracteres)")
    password_confirm: str
    organization_name: str = Field(..., min_length=1, max_length=255, description="Nombre de la organización")
    admin_first_name: str = Field(..., min_length=1, max_length=50, description="Nombre(s) del administrador de la cuenta de la organización")
    admin_last_name: str = Field(..., min_length=1, max_length=50, description="Apellido paterno del administrador de la cuenta de la organización")
    admin_slast_name: str | None = Field(default=None, min_length=1, max_length=50, description="Apellido materno del administrador de la cuenta de la organización (opcional)")
    biography: str | None = Field(default=None, min_length=1, description="Descripción o biografía de la organización (opcional)")

    @model_validator(mode="after")
    def check_passwords_match(self) -> "OrganizationCreate":
        if self.password != self.password_confirm:
            raise PydanticCustomError(
                'passwords_mismatch',  # Un código de error único que tú inventas
                'Las contraseñas no coinciden'  # El mensaje exacto que quieres mostrar
            )
        
        return self

class OrganizationRead(SQLModel):
    id_organization: int
    id_user: UUID
    organization_name: str
    admin_first_name: str
    admin_last_name: str 
    admin_slast_name: str | None = None
    biography: str | None = None
    photo_url: str | None = None

class OrganizationCreated(SQLModel):
    jwt: str | None = None
    id_organization: int
    id_user: UUID
    organization_name: str
    admin_first_name: str
    admin_last_name: str 
    admin_slast_name: str | None = None
    biography: str | None = None
    photo_url: str | None = None

    def get_admin_full_name(self) -> str:
        fullname: str = f"{self.admin_first_name} {self.admin_last_name}"
        if self.admin_slast_name:
            fullname += f" {self.admin_slast_name}"
        return fullname