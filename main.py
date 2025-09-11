from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from services.user import get_current_active_user, sign_in
from schemas import credentials
from typing import Any

app = FastAPI()

load_dotenv()

@app.get('/')
def index() -> dict:
    return {"Hello": "MyPetGuide"}

@app.post('/signin')
def signin(credentials: credentials.Credentials):
    return sign_in(email=credentials.email, password=credentials.password)


@app.get('/health')
def health() -> dict:
    return {'status': "ok"}

@app.get('/protegida')
def ruta_protegida(current_user: dict[str, Any] = Depends(get_current_active_user)) -> dict[str, Any]:
    return {"mensaje": f"Hola, {current_user.get('email')}"}