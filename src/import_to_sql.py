import os
import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION ---
# Adjust SERVER_NAME to match your SSMS connection ('localhost' or '.\SQLEXPRESS')
SERVER_NAME = "localhost"
DATABASE_NAME = "ManufacturingKPI"

# Connection string using Windows Authentication
CONN_STR = f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(CONN_STR)

RAW_DATA_DIR = os.path.join("data", "raw")

def process_and_load_mes(file_path, file_name):
    """Cleans and unpivots wide-format MES matrix files into SSMS."""
    print(f"Processing MES File: {file_path}...")
    df = pd.read_excel(file_path)

    # 1. First column contains the operating status (RUN, No WIP, Tool Cleaning, etc.)
    category_col = df.columns[0]

    #2. Unpivot equipment columns into key-value pairs
    df_melted = pd.melt(
        df,
        id_vars=[category_col],
        var_name="EquipmentName",
        value_name="TimePercentage"
    )

    # 3. Clean up column names and data types
    df_melted.rename(columns={category_col: "Category"}, inplace=True)
    df_melted.dropna(subset=["TimePercentage"], inplace=True)
    df_melted["TimePercentage"] = pd.to_numeric(df_melted["TimePercentage"], errors="coerce")
    df_melted["EquipmentName"] = df_melted["EquipmentName"].astype(str).str.strip()
    df_melted["SourceFileName"] = file_name

    # 4. Insert into SQL Server
    df_melted.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df_melted)} rows into Fact_EquipmentState.")

def process_and_load_sap(file_path, file_name):
    """Cleans standard relational SAP goods movement logs into SSMS."""
    print(f"Processing SAP File: {file_name}...")
    df = pd.read_excel(file_path)

    # 1. Map Excel headers to SQL column names
    column_mapping = {
        "Plant": "Plant",
        "Storage location": "StorageLocation",
        "Movement type": "MovementType",
        "Material": "MaterialCode",
        "Material Description": "MaterialDescription",
        "Batch": "Batch",
        "Quantity": "Quantity",
        "Unit of Entry": "UnitOfEntry",
        "Posting Date": "PostingDate",
        "Material Document": "MaterialDocument"
    }

    # Keep only target columns that exist in the sheet
    existing_cols = [col for col in column_mapping.keys() if col in df.columns]
    df_clean = df[existing_cols].rename(columns=column_mapping)

    # 2. Data type conversions
    if "PostingDate" in df_clean.columns:
        df_clean["PostingDate"] = pd.to_datetime(df_clean["PostingDate"]).dt.date
    if "Quantity" in df_clean.columns:
        df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce")
    if "MovementType" in df_clean.columns:
        df_clean["MovementType"] = pd.to_numeric(df_clean["MovementType"], errors="coerce")

    df_clean["SourceFileName"] = file_name

    # 3. Insert into SQL Server
    df_clean.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df_clean)} rows into Fact_SAP_MaterialMovement.")

def main():
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Directory '{RAW_DATA_DIR}' not found. Please create it and add your Excel files.")
        return

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(('.xlsx', '.xls'))]
    if not files:
        print(f"No Excel files found in '{RAW_DATA_DIR}'. Drop your files there first.")
        return

    for file_name in files:
        file_path = os.path.join(RAW_DATA_DIR, file_name)

        # Route processing based on file type/name
        if "SAP" in file_name.upper() or "311" in file_name or "P313" in file_name:
            process_and_load_sap(file_path, file_name)
        else:
            # Default to MES matrix layout for Tabber/Layup files
            process_and_load_mes(file_path, file_name)

if __name__ == "__main__":
    main()