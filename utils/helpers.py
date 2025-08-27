from sqlmodel import create_engine
from sqlalchemy.engine import Engine
import os

def get_database_credentials() -> dict[str, str]:
    return {
        "user": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_DATABASE"),
        "sslmode": "require"
    }

def get_engine() -> Engine:

    credentials: dict[str, str] = get_database_credentials()

    # Construct the SQLAlchemy connection string
    DATABASE_URL: str = f"postgresql+psycopg2://{credentials.get("user")}:{credentials.get("password")}@{credentials.get("host")}:{credentials.get("port")}/{credentials.get("database")}?sslmode={credentials.get("sslmode")}"

    return create_engine(DATABASE_URL)