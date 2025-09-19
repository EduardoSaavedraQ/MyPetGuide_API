from sqlmodel import SQLModel, Field
from pydantic import EmailStr, model_validator
from pydantic_core import PydanticCustomError


class LoginForm(SQLModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, max_length=16, description="Contraseña del usuario (8-16 caracteres)")

class SignUpForm(SQLModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, max_length=16, description="Contraseña del usuario (8-16 caracteres)")
    password_confirm: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> "SignUpForm":
        if self.password != self.password_confirm:
            raise PydanticCustomError(
                'passwords_mismatch',  # Un código de error único que tú inventas
                'Las contraseñas no coinciden'  # El mensaje exacto que quieres mostrar
            )
        
        return self