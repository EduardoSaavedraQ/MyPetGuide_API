from sqlmodel import create_engine
from supabase import Client
import os

def get_engine() -> create_engine:

    USER = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    DBNAME = os.getenv("DB_DATABASE")

    # Construct the SQLAlchemy connection string
    DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

    return create_engine(DATABASE_URL)