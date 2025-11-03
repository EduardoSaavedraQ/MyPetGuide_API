from sqlmodel import SQLModel, Field

class AdoptionCreate(SQLModel):
    id_requester: str = Field(..., description="UUID del usuario que busca adoptar la mascota")
    id_pet: int = Field(..., description="Identificador de la mascota que se quiere dar en adopción")