from sqlmodel import text
from utils.helpers import get_engine
from dotenv import load_dotenv
load_dotenv()

def test_get_database_connection() -> None:

    with get_engine().connect() as conn:
        result = conn.execute(text("SELECT version()"))  
        
        assert result.scalar() == "PostgreSQL 17.4 on aarch64-unknown-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit"