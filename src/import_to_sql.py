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

    xls = pd.ExcelFile(file_path)

    # Iterate over sheets to find a tabular sheet, or parse the Pivot Table sheet
    target_sheet = None
    for sheet in xls.sheet_names:
        if any(term in sheet.lower() for term in ["raw", "data", "list", "detail"]):
            target_sheet = sheet
            break

    if target_sheet:
        print(f" -> Reading detailed tab: '{target_sheet}'")
        df = pd.read_excel(file_path, sheet_name=target_sheet)
    else:
        df = pd.read_excel(file_path, sheet_name=0)

    df.columns = df.columns.astype(str).str.strip().str.replace('\n', ' ')
    cols_upper = [str(c).upper() for c in df.columns]

    df_clean = pd.DataFrame()

    # Helper function to find standard SAP columns flexible by keyword
    def find_col(keywords):
        for col in df.columns:
            col_str = str(col).upper().strip()
            for kw in keywords:
                if kw == col_str or kw in col_str:
                    return col
        return None

    # Case 1: Excel Pivot Table Layout
    if "ROW LABELS" in cols_upper or "PCS" in cols_upper:
        print(" -> Detected Pivot Table Summary Layout")
        row_col = find_col(["ROW LABELS", "ROW"])
        pcs_col = find_col(["PCS"])

        if row_col and pcs_col:
            parent_rows = df[df[row_col].astype(str).str.startswith("MD06", na=False)].copy()
            df_clean["Plant"] = "P313"
            df_clean["StorageLocation"] = "PROD"
            df_clean["MovementType"] = 101
            df_clean["MaterialCode"] = parent_rows[row_col].astype(str).str.strip()
            df_clean["MaterialDescription"] = "Production Volume Output"
            df_clean["Quantity"] = pd.to_numeric(
                parent_rows[pcs_col].astype(str).str.replace('-', '0').str.replace(',', ''),
                errors="coerce"
            )
            df_clean["UnitOfEntry"] = "PCS"
            df_clean["PostingDate"] = pd.Timestamp.now().date()

    # Case 2: Wide Matrix Sheet
    elif any(k in cols_upper for k in ["MATERIAL CODE", "SUM.TOTAL", "[WT]SUM.TOTAL"]):
        print(" -> Detected Production Volume / Summary Matrix Layout")
        mat_col = find_col(["MATERIAL CODE", "MATERIAL"])
        qty_col = find_col(["SUM.TOTAL", "SUM.GR", "[WT]SUM.TOTAL"])

        df_clean["Plant"] = "P313"
        df_clean["StorageLocation"] = "PROD"
        df_clean["MovementType"] = 101
        df_clean["MaterialCode"] = df[mat_col].astype(str).str.strip() if mat_col else None
        df_clean["MaterialDescription"] = "Production Volume Output"
        df_clean["Quantity"] = pd.to_numeric(df[qty_col], errors="coerce") if qty_col else 0
        df_clean["UnitOfEntry"] = "PCS"
        df_clean["PostingDate"] = pd.Timestamp.now().date()

    # Case 3: Transactional Goods Movement Log
    else:
        print(" -> Detected Transactional Goods Movement Layout")

        col_plant = find_col(["PLANT"])
        col_sloc = find_col(["STORAGE LOCATION", "STOR. LOC.", "SLOC", "STORAGE LOC"])
        col_mvt = find_col(["MOVEMENT TYPE", "MVT", "MOVE TYPE"])
        col_mat = find_col(["MATERIAL CODE", "MATERIAL"])
        col_desc = find_col(["MATERIAL DESCRIPTION", "MAT DESCRIPTION", "MATERIAL DESC"])
        col_qty = find_col(["QUANTITY", "QTY"])
        col_uom = find_col(["UNIT OF ENTRY", "UNE", "BUN", "UOM", "UNIT"])
        col_date = find_col(["POSTING DATE", "POST. DATE", "ENTRY DATE"])
        col_doc = find_col(["MATERIAL DOCUMENT", "MAT. DOC.", "DOCUMENT NO"])

        df_clean["Plant"] = df[col_plant].astype(str).str.strip() if col_plant else "P313"
        df_clean["StorageLocation"] = df[col_sloc].astype(str).str.strip() if col_sloc else None
        df_clean["MovementType"] = df[col_mvt] if col_mvt else None
        df_clean["MaterialCode"] = df[col_mat].astype(str).str.strip() if col_mat else None
        df_clean["MaterialDescription"] = df[col_desc].astype(str).str.strip() if col_desc else None
        df_clean["Quantity"] = pd.to_numeric(df[col_qty], errors="coerce") if col_qty else 0
        df_clean["UnitOfEntry"] = df[col_uom].astype(str).str.strip() if col_uom else "PCS"

        if col_date:
            df_clean["PostingDate"] = pd.to_datetime(df[col_date], errors="coerce").dt.date
        else:
            df_clean["PostingDate"] = pd.Timestamp.now().date()

        if col_doc:
            df_clean["MaterialDocument"] = df[col_doc].astype(str).str.strip()

    # Fill fallback Plant if null values remain
    df_clean["Plant"] = df_clean["Plant"].fillna("P313")

    # --- Common Cleanup ---
    if "Quantity" in df_clean.columns:
        df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce")
        df_clean = df_clean[df_clean["Quantity"] > 0].copy()

    subset_cols = [col for col in ["MaterialCode", "Quantity"] if col in df_clean.columns]
    if subset_cols:
        df_clean.dropna(subset=subset_cols, inplace=True)

    df_clean["SourceFileName"] = file_name

    if df_clean.empty:
        print(f" Warning: No valid rows processed from {file_name}. Skipping insert.")
        return

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