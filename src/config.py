"""SQL Server connection settings. Keep credentials outside source code."""

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine


def get_db_engine():
    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_NAME", "ManufacturingKPI")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    auth = os.getenv("DB_AUTH", "windows").lower()

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        "Encrypt=yes",
        f"TrustServerCertificate={os.getenv('DB_TRUST_CERT', 'no')}",
    ]

    if auth == "sql":
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        if not username or not password:
            raise ValueError("DB_USER and DB_PASSWORD must be set for SQL authentication")
        parts.extend([f"UID={username}", f"PWD={password}"])
    else:
        parts.append("Trusted_Connection=yes")

    return create_engine("mssql+pyodbc:///?odbc_connect=" + quote_plus(";".join(parts)))
