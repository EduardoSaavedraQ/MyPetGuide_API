from sqlmodel import SQLModel, Field
from schemas.pet import PetChatInfo
from schemas.users import UserPublicInfo
from schemas.organization import OrganizationRead

class ChatCreate(SQLModel):
    """Modelo para crear una nueva sala de chat entre un solicitante y el dueño de una mascota.

    Este modelo representa los datos mínimos necesarios para iniciar un chat de adopción:
    el identificador del dueño actual y el identificador de la mascota que se desea adoptar.
    El id_requester se obtiene automáticamente del token JWT del usuario autenticado.
    """

    id_owner: str = Field(..., description="UUID de la cuenta a la cual pertenece la mascota que se busca adoptar.")
    id_pet: int = Field(..., description="Identificador único de la mascota que se desea adoptar.")

class ChatCreated(SQLModel):
    """Respuesta tras crear exitosamente una sala de chat.

    Contiene los identificadores necesarios para referenciar la sala de chat y
    a todos los participantes (solicitante, dueño y mascota).
    """

    id_room: int
    id_pet: int
    id_requester: str
    id_owner: str

class ChatRead(SQLModel):
    """Modelo base para la lectura de salas de chat.

    Contiene la información básica presente en cualquier vista de chat:
    el identificador de la sala y la información básica de la mascota.
    Este modelo sirve como base para las vistas específicas de chat entrante y saliente.
    """

    id_room: int
    pet: PetChatInfo

class ChatReadOutcomming(ChatRead):
    """Modelo para las salas de chat donde el usuario autenticado es el dueño.

    Extiende ChatRead agregando la información del usuario solicitante,
    que puede ser un usuario individual u organización.
    """

    owner: UserPublicInfo | OrganizationRead | None = None

class ChatReadIncomming(ChatRead):
    """Modelo para las salas de chat donde el usuario autenticado es el dueño.

    Extiende ChatRead agregando la información del usuario solicitante,
    que puede ser un usuario individual u organización.
    """

    requester: UserPublicInfo | OrganizationRead | None = None