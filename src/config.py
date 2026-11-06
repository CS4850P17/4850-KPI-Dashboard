import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus

def get_db_engine():
    """
    Attempts to connect to Azure SQL Server. If connection fails or is disabled,
    falls back gracefully to local SQLite.
    """
    use_sqlite_forced = os.getenv("USE_SQLITE", "false").lower() == "true"

    if not use_sqlite_forced:
        try:
            # Azure SQL Server Configuration
            server = os.getenv("DB_SERVER", "qcells-team3.database.windows.net")
            database = os.getenv("DB_NAME", "qcells-database")
            driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
            username = os.getenv("DB_USER", "team3")
            password = os.getenv("DB_PASSWORD", "Blueberry123")

            params = quote_plus(
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            azure_url = f"mssql+pyodbc:///?odbc_connect={params}"
            engine = create_engine(azure_url)
            
            # Test the connection immediately
            with engine.connect() as conn:
                pass
            print(" Connected successfully to Azure SQL Server.")
            return engine
            
        except Exception as e:
            print(f"⚠️ Azure SQL connection failed ({e}). Falling back to local SQLite...")

    # Fallback / Default: Local SQLite
    db_file = os.getenv("DB_FILE", "manufacturing_kpi.db")
    print(f"📁 Using local SQLite database: {db_file}")
    return create_engine(f"sqlite:///{db_file}")