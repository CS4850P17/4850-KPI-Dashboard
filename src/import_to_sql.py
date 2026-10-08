import os
import urllib
import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION ---
# Use a raw string r"..." to fix SyntaxWarning with backslashes
SERVER_NAME = r"CHOPPER\SQLEXPRESS"
DATABASE_NAME = "ManufacturingKPI"

# Connection string setup
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

CONN_STR = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(CONN_STR)

RAW_DATA_DIR = os.path.join("data", "raw")

def process_and_load_mes(file_path, file_name):
    """Cleans and unpivots wide-format MES matrix files into SSMS."""
    print(f"Processing MES File: {file_path}...")
    df = pd.read_excel(file_path)

    # 1. First column contains the operating status (RUN, No WIP, Tool Cleaning, etc.)
    category_col = df.columns[0]

    # Drop rows where the Category itself is missing/null (e.g., blank total rows)
    df = df.dropna(subset=[category_col]).copy()

    # Clean string spaces in Category
    df [category_col] = df[category_col].astype(str).str.strip()

    # Filter out empty strig rows or total summary rows if necessary
    df = df[df[category_col] != ""].copy()

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

    # Filter out summary columns like 'average' if you only want machine-level data
    df_melted = df_melted[df_melted["EquipmentName"].str.lower() != "average"]

    # 4. Insert into SQL Server
    df_melted.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df_melted)} rows into Fact_EquipmentState.")

def process_and_load_sap(file_path, file_name):
    """Cleans both transactional goods movement logs and production column sheets into SSMS."""
    print(f"Processing SAP File: {file_name}...")
    df = pd.read_excel(file_path)

    # Strip whitespace from Excel column names
    df.columns = df.columns.astype(str).str.strip()

    # Case 1: Production Volume / Matrix Sheet (SAP 3)
    if "Material Code" in df.columns or "Sum.Total" in df.columns:
        print(" -> Detected Production Volume / Summary Sheet Layout")

        # Map to SQL Schema
        df_clean = pd.DataFrame()
        df_clean["Plant"] = "P313" # Default plant context
        df_clean["StorageLocation"] = "PRT3"
        df_clean["MovementType"] = 311 # Standard Goods Receipt / Production output

        # Map Material fields
        if "Material Code" in df.columns:
            df_clean["Material Code"] = df["Material Code"].astype(str).str.strip()
        elif "Material" in df.columns:
            df_clean["MaterialCode"] = df["Material"].astype(str).str.strip()

        df_clean["MaterialDescription"] = "Production Volume Output"

        # Map Quantity & Unit
        if "Sum.Total" in df.columns:
            df_clean["Quantity"] = pd.to_numeric(df["Sum.Total"], errors="coerce")
        elif "[WT]Sum.Total" in df.columns:
            df_clean["Quantity"] = pd.to_numeric(df["[WT]Sum.Total"], errors="coerce")

        if "Base unit of Measure" in df.columns:
            df_clean["UnitOfEntry"] = df["Base unit of Measure"].astype(str).str.strip()

        # Default posting date to today/tile date if missing from matrix sheet
        df_clean["PostingDate"] = pd.Timestamp.now().date()

    # Case 2: Standard Transactional Movement Log (SAP 2)
    else:
        print(" -> Detected Transactional Goods Movement Layout")
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

        rename_dict = {col: column_mapping[col] for col in df.columns if col in column_mapping}
        df_clean = df[list(rename_dict.keys())].rename(columns=rename_dict)

        if "Plant" not in df_clean.columns:
            df_clean["Plant"] = "P313"

        if "PostingDate" in df_clean.columns:
            df_clean["PostingDate"] = pd.to_datetime(df_clean["PostingDate"], errors="coerce").dt.date

    # --- Common Cleanup ---
    if "Quantity" in df_clean.columns:
        df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce")
    if "MovementType" in df_clean.columns:
        df_clean["MovementType"] = pd.to_numeric(df_clean["MovementType"], errors="coerce")

    # Drop rows without material code or valid quantity
    df_clean.dropna(subset=["MaterialCode", "Quantity"], inplace=True)
    df_clean=df_clean[df_clean["Quantity"] > 0].copy()

    df_clean["SourceFileName"] = file_name

    # Load into SSMS
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