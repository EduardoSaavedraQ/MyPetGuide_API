from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def index() -> dict:
    return {"Hello": "MyPetGuide"}

@app.get('/health')
def health() -> dict:
    return {'status': "ok"}