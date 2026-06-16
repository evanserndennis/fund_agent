import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / 'ledger.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.OperationalError as e:
        raise e