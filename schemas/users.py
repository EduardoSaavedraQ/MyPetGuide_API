from sqlmodel import SQLModel, Field
from schemas.auth import SignUpForm
from uuid import UUID

class UserCreate(SignUpForm):
    """Modelo para la validación de datos al crear un nuevo usuario.

    Hereda de `SignUpForm` para reutilizar la validación de credenciales
    (email y contraseñas) y añade los campos con el nombre del usuario.

    Attributes:
        first_name (str): Nombre(s) del usuario.
        last_name (str): Apellido paterno del usuario.
        slast_name (str | None): Apellido materno del usuario (opcional).
        
    Los campos `email`, `password` y `password_confirm` son heredados de `SignUpForm`.

    Raises:
        PydanticCustomError: Se lanza si las contraseñas no coinciden (comportamiento
                            heredado de `SignUpForm`).
    """

    first_name: str = Field(..., min_length=1, max_length=50, description="Nombre(s) del usuario")
    last_name: str = Field(..., min_length=1, max_length=50, description="Apellido paterno del usuario")
    slast_name: str | None = Field(default=None, min_length=1, max_length=50, description="Apellido materno del usuario (opcional)")

class UserRead(SQLModel):
    """Representa el perfil completo de un usuario con sus preferencias para mascotas.

    Este modelo define la estructura completa de los datos de un usuario, incluyendo
    su información personal y todas las características relevantes para determinar
    la compatibilidad con una mascota.

    Attributes:
        id_profile (int): Identificador único del perfil del usuario.
        id_user (UUID): Identificador único de la cuenta de usuario en el sistema de autenticación.
        first_name (str): Nombre(s) del usuario.
        last_name (str): Apellido paterno del usuario.
        slast_name (str | None): Apellido materno del usuario (opcional).
        photo_url (str | None): URL de la foto de perfil del usuario.
        house_size (int | None): Tamaño de la casa en metros cuadrados.
        house_backyard_size (int | None): Tamaño del patio o área exterior en metros cuadrados.
        family_size (int | None): Número de personas en la familia.
        has_kids (bool | None): Indica si hay niños en casa.
        has_neighbors (bool | None): Indica si hay vecinos cercanos.
        available_time_per_day (int | None): Horas al día disponibles para la mascota.
        vet_access (bool | None): Indica si se tiene fácil acceso a un veterinario.
        has_other_pets (bool | None): Indica si ya existen otras mascotas en el hogar.
        experience_with_pets (int | None): Nivel de experiencia cuidando mascotas.
        preferred_species (bool | None): Especie preferida (True para perro, False para gato).
    """

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
        """Construye y devuelve el nombre completo del usuario."""
        fullname: str = f"{self.first_name} {self.last_name}"
        if self.slast_name:
            fullname += f" {self.slast_name}"
        return fullname

class UserCreated(UserRead):
    """Representa la respuesta exitosa al crear un nuevo usuario.

    Hereda todos los campos de `UserRead` y añade un token JWT para que el
    cliente pueda autenticar sesiones futuras de inmediato.

    Attributes:
        jwt (str | None): Token de acceso JWT para la sesión del nuevo usuario.
                        Los demás atributos son heredados de `UserRead`.
    """

    jwt: str | None = None

class UserProfileCreate(SQLModel):
    """Modelo para crear o actualizar el perfil de compatibilidad de un usuario.

    Contiene todos los campos relacionados con el estilo de vida y las preferencias
    de un usuario para determinar su afinidad con diferentes tipos de mascotas.
    No incluye datos personales como el nombre o el ID.

    Attributes:
        house_size (int | None): Tamaño de la casa en m² (mínimo 40).
        house_backyard_size (int | None): Tamaño del patio en m² (mínimo 0).
        family_size (int | None): Número de personas en la familia (mínimo 1).
        has_kids (bool | None): Indica si hay niños en la familia.
        has_neighbors (bool | None): Indica si hay vecinos cerca.
        available_time_per_day (int | None): Horas disponibles al día para la mascota (1-24).
        vet_access (bool | None): Indica si se tiene acceso a un veterinario.
        has_other_pets (bool | None): Indica si ya se tienen otras mascotas.
        experience_with_pets (int | None): Nivel de experiencia cuidando mascotas.
        preferred_species (bool | None): Preferencia de especie (True=perro, False=gato).
    """

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