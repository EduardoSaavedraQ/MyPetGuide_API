from sqlmodel import SQLModel, Field
from uuid import UUID

class OrganizationCreate(SQLModel):
    organization_name: str = Field(..., min_length=1, max_length=255, description="Nombre de la organización")
    admin_first_name: str = Field(..., min_length=1, max_length=50, description="Nombre(s) del administrador de la cuenta de la organización")
    admin_last_name: str = Field(..., min_length=1, max_length=50, description="Apellido paterno del administrador de la cuenta de la organización")
    admin_slast_name: str | None = Field(default=None, min_length=1, max_length=50, description="Apellido materno del administrador de la cuenta de la organización (opcional)")
    biography: str | None = Field(default=None, min_length=1, description="Descripción o biografía de la organización (opcional)")

class OrganizationRead(SQLModel):
    id_organization: int
    id_user: UUID
    organization_name: str
    admin_first_name: str
    admin_last_name: str 
    admin_slast_name: str | None
    biography: str | None
    photo_url: str | None