from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class Credentials(SQLModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, max_length=16, description="Contraseña del usuario (8-16 caracteres)")