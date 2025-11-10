from sqlmodel import SQLModel, Field
from uuid import UUID
from schemas.auth import SignUpForm

class OrganizationUpdate(SQLModel):
    """Modelo para la validación de datos al editar el perfil de una organización existente.

    Este modelo define la estructura de los datos que se ven implicados en el proceso de
    actualización del perfil de una organización.

    Attributes:
        organization_name (str): Nombre de la organización.
        admin_first_name (str): Nombre(s) del administrador.
        admin_last_name (str): Apellido paterno del administrador.
        admin_slast_name (str | None): Apellido materno del administrador (opcional).
        biography (str | None): Biografía o descripción de la organización (opcional).
    """

    organization_name: str = Field(..., min_length=1, max_length=255, description="Nombre de la organización")
    admin_first_name: str = Field(..., min_length=1, max_length=50, description="Nombre(s) del administrador de la cuenta de la organización")
    admin_last_name: str = Field(..., min_length=1, max_length=50, description="Apellido paterno del administrador de la cuenta de la organización")
    admin_slast_name: str | None = Field(default=None, min_length=1, max_length=50, description="Apellido materno del administrador de la cuenta de la organización (opcional)")
    biography: str | None = Field(default=None, min_length=1, description="Descripción o biografía de la organización (opcional)")

class OrganizationCreate(SignUpForm, OrganizationUpdate):
    """Modelo para la validación de datos al crear una nueva organización.

    Hereda de `SignUpForm` para reutilizar la validación de credenciales
    (email y contraseñas) y hereda también de `OrganizationUpdate` para reutilizar la validación de los
    datos de perfil de organización.

    Raises:
        PydanticCustomError: Se lanza si las contraseñas no coinciden (comportamiento
                            heredado de `SignUpForm`).
    """

    pass

class OrganizationRead(SQLModel):
    """Modelo para representar los datos públicos de una organización.

    Esta clase define la estructura de datos estándar para mostrar la información
    de un perfil de organización. Se utiliza como base para otras representaciones
    y como respuesta en endpoints de consulta (ej. "obtener perfil").

    Attributes:
        id_organization (int): Identificador único del perfil de la organización.
        id_user (UUID): Identificador único de la cuenta de usuario asociada.
        organization_name (str): Nombre de la organización.
        admin_first_name (str): Nombre(s) del administrador.
        admin_last_name (str): Apellido paterno del administrador.
        admin_slast_name (str | None): Apellido materno del administrador (opcional).
        biography (str | None): Biografía de la organización (opcional).
        photo_url (str | None): URL de la imagen de perfil de la organización (opcional).
    """

    id_organization: int
    id_user: UUID
    organization_name: str
    admin_first_name: str
    admin_last_name: str 
    admin_slast_name: str | None = None
    biography: str | None = None
    photo_url: str | None = None

    def get_admin_full_name(self) -> str:
        """Construye y devuelve el nombre completo del administrador.

        Concatena el nombre, apellido paterno y, si existe, el apellido materno
        para formar una sola cadena de texto.

        Returns:
            str: El nombre completo del administrador.
        """

        fullname: str = f"{self.admin_first_name} {self.admin_last_name}"
        if self.admin_slast_name:
            fullname += f" {self.admin_slast_name}"
        return fullname

class OrganizationCreated(OrganizationRead):
    """Representa la respuesta exitosa al crear una nueva organización.

    Hereda todos los campos de `OrganizationRead` y añade un token JWT para que el
    cliente pueda autenticar sesiones futuras de inmediato.

    Attributes:
        jwt (str): Token de acceso JWT para la sesión del nuevo usuario.
        refresh_token: Token que permite refrescar la sesión del usuario.

    Los demás atributos son heredados de `OrganizationRead`.
    """

    jwt: str
    refresh_token: str