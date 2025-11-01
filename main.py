from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from services.auth import get_current_active_user
from typing import Any
from routers import auth, organization, user, pet, pets, public_profile, chat


app = FastAPI()

app.include_router(auth.router)
app.include_router(organization.router)
app.include_router(user.router)
app.include_router(pet.router)
app.include_router(pets.router)
app.include_router(public_profile.router)
app.include_router(chat.router)


load_dotenv()

@app.get('/')
def index() -> dict:
    return {"Hello": "MyPetGuide"}

@app.get('/health')
def health() -> dict:
    return {'status': "ok"}

@app.get('/protegida')
def ruta_protegida(current_user: dict[str, Any] = Depends(get_current_active_user)) -> dict[str, Any]:
    return {"mensaje": f"Hola, {current_user.get('email')}"}