import os
from sqlalchemy import create_engine

# Local SQLite file database (Bypasses Azure ODBC / OpenSSL driver conflicts entirely)
DB_FILE = "manufacturing_kpi.db"
CONN_STR = f"sqlite:///{DB_FILE}"

def get_db_engine():
    return create_engine(CONN_STR)