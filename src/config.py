
import os
import urllib.parse

from sqlalchemy import create_engine


def get_db_engine():
    """
    Create a SQLAlchemy engine for Azure SQL Database.

    Connection settings are read from environment
    variables. No credentials are stored in source code.
    """

    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    driver = os.getenv(
        "DB_DRIVER",
        "ODBC Driver 18 for SQL Server"
    )

    # Validate required configuration
    missing = [
        name
        for name, value in {
            "DB_SERVER": server,
            "DB_NAME": database,
            "DB_USER": username,
            "DB_PASSWORD": password,
        }.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )

    # Build Azure SQL connection string
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

    encoded_params = urllib.parse.quote_plus(
        connection_string
    )

    engine = create_engine(
        "mssql+pyodbc:///?odbc_connect="
        + encoded_params
    )

    return engine
