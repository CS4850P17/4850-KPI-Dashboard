import os
import urllib
from sqlalchemy import create_engine

# Run with Azure SQL Server and not locally
USE_AZURE = True

SERVER_NAME = "qcells-team3.database.windows.net"
DATABASE_NAME = "qcells-database"
DB_USER = "team3"
DB_PASS = "Blueberry123"

def get_db_engine():
    if USE_AZURE:
        params = urllib.parse.quote_plus(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DATABASE_NAME};"
            f"UID={DB_USER};pwd={DB_PASS};"
            f"TrustServerCertificate=yes;"
        )
        conn_str = f"mssql+pyodbc:///?odbc_connect={params}"
    else:
        conn_str = "sqlite:///manufacturing_kpi.db"

    return create_engine(conn_str)
