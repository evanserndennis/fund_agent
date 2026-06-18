import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "fund_agent"),
        user=os.getenv("POSTGRES_USER", "fund_admin"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )