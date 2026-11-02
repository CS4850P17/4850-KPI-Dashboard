"""SQL Server connection settings. Keep credentials outside source code."""

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

def get_db_engine():
    """Returns the SQLAlchemy engine connected to Azure SQL or local configuration."""
    # Use environment variables if set, otherwise fallback to your team's Azure SQL instance
    server = os.getenv("DB_SERVER", "qcells-team3.database.windows.net")
    database = os.getenv("DB_NAME", "qcells-database")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # Check if SQL auth or Windows auth is preferred
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