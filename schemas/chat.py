from sqlmodel import SQLModel, Field

class ChatCreate(SQLModel):
    id_owner: str = Field(..., description="UUID de la cuenta a la cual pertenece la mascota que se busca adoptar.")
    id_pet: int = Field(..., description="Identificador único de la mascota que se desea adoptar.")

class ChatRead(SQLModel):
    id_room: int
    id_pet: int
    id_requester: str
    id_owner: str

class ChatReadWithFinishedField(ChatRead):
    finished: bool