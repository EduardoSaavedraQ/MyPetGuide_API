from sqlmodel import SQLModel, Field
from schemas.pet import PetChatInfo
from schemas.users import UserPublicInfo
from schemas.organization import OrganizationRead

class ChatCreate(SQLModel):
    id_owner: str = Field(..., description="UUID de la cuenta a la cual pertenece la mascota que se busca adoptar.")
    id_pet: int = Field(..., description="Identificador único de la mascota que se desea adoptar.")

class ChatCreated(SQLModel):
    id_room: int
    id_pet: int
    id_requester: str
    id_owner: str

class ChatRead(SQLModel):
    id_room: int
    pet: PetChatInfo

class ChatReadOutcomming(ChatRead):
    owner: UserPublicInfo | OrganizationRead | None = None

class ChatReadIncomming(ChatRead):
    requester: UserPublicInfo | OrganizationRead | None = None

class ChatReadWithFinishedField(ChatRead):
    finished: bool