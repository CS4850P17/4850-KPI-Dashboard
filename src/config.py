
"""
Database configuration for the KPI Dashboard.

Supports:
- SQLite for local development
- Azure SQL Database for shared deployment

Credentials are loaded from environment variables.
"""

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine


def get_db_engine():
    # Local development mode
    use_sqlite = (
        os.getenv("USE_SQLITE", "true").lower() == "true"
    )

    if use_sqlite:
        db_file = os.getenv(
            "DB_FILE",
            "manufacturing_kpi.db"
        )

        return create_engine(f"sqlite:///{db_file}")

    # Azure SQL configuration
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    driver = os.getenv(
        "DB_DRIVER",
        "ODBC Driver 18 for SQL Server"
    )

    required = {
        "DB_SERVER": server,
        "DB_NAME": database,
        "DB_USER": username,
        "DB_PASSWORD": password,
    }

    missing = [
        name for name, value in required.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    return create_engine(
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(connection_string)
    )
