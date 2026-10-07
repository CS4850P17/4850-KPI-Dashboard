import os
from sqlalchemy import create_engine

# Database connection settings
# adjust server name and database name to match SQL server instance
SERVER = os.gatenv("DB_SERVER", "localhost")
DATABASE = os.gatenv("DB_NAME", "ManufacturingKPI")
DRIVER = "ODBC Driver 17 for SQL Server"

# SQLAlchemy connection string using Windows Authentication
CONN_STR = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver={DRIVER}&trusted_connection=yes"

def get_db_engine():
  return create_engine(CONN_STR)
