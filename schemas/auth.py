from sqlmodel import SQLModel, Field
from pydantic import EmailStr, model_validator
from pydantic_core import PydanticCustomError

class LoginForm(SQLModel):
    """Valida las credenciales para el inicio de sesión.

    Esta clase define la estructura y las validaciones básicas para los datos
    enviados en un formulario de inicio de sesión de un usuario.

    Attributes:
        email (EmailStr): Correo electrónico del usuario.
        password (str): Contraseña del usuario (entre 8 y 16 caracteres).
    """

    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, max_length=16, description="Contraseña del usuario (8-16 caracteres)")

class SignUpForm(LoginForm):
    """Valida los datos para la creación de una nueva cuenta.

    Hereda los campos `email` y `password` de `LoginForm` y añade la confirmación
    de la contraseña, junto con una validación para asegurar que ambas coincidan.

    Attributes:
        password_confirm (str): Campo de confirmación que debe coincidir con `password`.

    Los demás atributos son heredados de `LoginForm`.
    
    Raises:
        PydanticCustomError: Se lanza si los campos `password` y `password_confirm` no coinciden.
    """

    password_confirm: str = Field(..., min_length=8, max_length=16, description="Campo de confirmación de contraseña (8-16 caracteres)")

    @model_validator(mode="after")
    def check_passwords_match(self) -> "SignUpForm":
        """Valida que las contraseñas proporcionadas coincidan."""
        if self.password != self.password_confirm:
            raise PydanticCustomError(
                'passwords_mismatch',  # Un código de error único que tú inventas
                'Las contraseñas no coinciden'  # El mensaje exacto que quieres mostrar
            )

        return self