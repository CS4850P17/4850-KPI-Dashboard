"""
Configuration Module for Qcells 4850 KPI Dashboard.
Handles database connections, supporting local SQLite for smooth development and Azure SQL Server for production deployment.
"""

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

def get_db_engine():
    """
    Returns the SQLAlchemy engine connected to either local SQLite 
    or Azure SQL Server depending on environment variables.
    """
    use_sqlite = os.getenv("USE_SQLITE", "true").lower() == "true"
    
    if use_sqlite:
        db_file = os.getenv("DB_FILE", "manufacturing_kpi.db")
        return create_engine(f"sqlite:///{db_file}")
    
    # Azure SQL Server Configuration
    server = os.getenv("DB_SERVER", "qcells-team3.database.windows.net")
    database = os.getenv("DB_NAME", "qcells-database")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    username = os.getenv("DB_USER", "team3")
    password = os.getenv("DB_PASSWORD", "Blueberry123")
    
    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"UID={username}",
        f"PWD={password}",
        "Encrypt=yes",
        "TrustServerCertificate=yes"
    ]

    return create_engine("mssql+pyodbc:///?odbc_connect=" + quote_plus(";".join(parts)))