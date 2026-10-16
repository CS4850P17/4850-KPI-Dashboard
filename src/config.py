import os
from sqlalchemy import create_engine

# Use a local SQLite database file for your student project
DB_FILE = "manufacturing_kpi.db"
CONN_STR = f"sqlite:///{DB_FILE}"

def get_db_engine():
    return create_engine(CONN_STR)