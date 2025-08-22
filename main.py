from fastapi import FastAPI
from sqlmodel import create_engine, text
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

@app.get('/')
def index() -> dict:
    return {"Hello": "MyPetGuide"}

@app.get('/health')
def health() -> dict:
    return {'status': "ok"}


@app.get('/test-database-connection')
def test_db_conn() -> dict:
    USER = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    DBNAME = os.getenv("DB_DATABASE")

    # Construct the SQLAlchemy connection string
    DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        return {"version": version}

