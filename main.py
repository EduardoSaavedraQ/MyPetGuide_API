from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from services.auth import login, get_current_active_user
from schemas.credentials import Credentials
from typing import Any

app = FastAPI()

load_dotenv()

@app.get('/')
def index() -> dict:
    return {"Hello": "MyPetGuide"}

@app.post('/login')
def signin(credentials: Credentials):
    return login(email=credentials.email, password=credentials.password)


@app.get('/health')
def health() -> dict:
    return {'status': "ok"}

@app.get('/protegida')
def ruta_protegida(current_user: dict[str, Any] = Depends(get_current_active_user)) -> dict[str, Any]:
    return {"mensaje": f"Hola, {current_user.get('email')}"}