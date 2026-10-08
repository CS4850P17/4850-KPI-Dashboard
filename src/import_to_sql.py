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
    """Processes MES / KPI report Excel files and loads cleaned records into Fact_EquipmentState."""
    print(f"Processing MES File: {file_path}...")
    xls = pd.ExcelFile(file_path)

    target_sheet = next(
        (s for s in xls.sheet_names if any(k in s.lower() for k in ["summary", "kpi", "raw", "data", "rate"])),
        xls.sheet_names[0]
    )

    df_raw = pd.read_excel(file_path, sheet_name=target_sheet, header=None)

    # Detect multi-level header layout (check first 10 rows for Product / KPI structures)
    header_idx = None
    for r in range(min(10, len(df_raw))):
        row_vals = [str(v).upper() for v in df_raw.iloc[r].values]
        if any("PRODUCT" in v or "TM_ALL" in v or "YIELD" in v or "OM_GOOD" in v for v in row_vals):
            header_idx = r
            break

    if header_idx is not None:
        # Load with detected header row and row above as multi-level header
        header_spec = [header_idx - 1, header_idx] if header_idx > 0 else header_idx
        df = pd.read_excel(file_path, sheet_name=target_sheet, header=header_spec)

        # Product Name is located at Column index 2 (Column C in KPI Summary layout)
        prod_col = df.columns[2]

        records = []
        for idx, row in df.iterrows():
            product_name = str(row[prod_col]).strip()

            # Filter out header/summary strings
            if not product_name or product_name.lower() in [
                'nan', 'none', 'total', 'product name', 'kr', 'cn', 'ctv', 'es', 'jc', 'rdm'
            ]:
                continue

            for col in df.columns:
                if col == prod_col:
                    continue

                if isinstance(col, tuple):
                    block_header = str(col[0]).strip()
                    sub_header = str(col[1]).strip()
                    metric_name = f"{block_header} - {sub_header}"
                else:
                    metric_name = str(col).strip()

                val = row[col]
                if pd.notna(val):
                    try:
                        clean_val = float(val)
                        records.append({
                            "Category": product_name,
                            "EquipmentName": metric_name,
                            "TimePercentage": clean_val,
                            "SourceFileName": file_name
                        })
                    except (ValueError, TypeError):
                        continue

        df_clean = pd.DataFrame(records)

    else:
        # Single-level matrix format
        df = pd.read_excel(file_path, sheet_name=target_sheet)
        df.columns = df.columns.astype(str).str.strip()

        cat_col = df.columns[0]
        value_vars = [c for c in df.columns if c != cat_col and not c.startswith("Unnamed:")]

        df_melted = df.melt(id_vars=[cat_col], value_vars=value_vars, var_name="EquipmentName",
                            value_name="TimePercentage")
        df_clean = df_melted.rename(columns={cat_col: "Category"})
        df_clean["SourceFileName"] = file_name

    # Post-Cleaning Guardrails
    if not df_clean.empty:
        df_clean["TimePercentage"] = pd.to_numeric(df_clean["TimePercentage"], errors="coerce").fillna(0.0)
        df_clean = df_clean[
            df_clean["Category"].notna() &
            (df_clean["Category"].astype(str).str.strip() != "") &
            ~df_clean["EquipmentName"].astype(str).str.contains("Unnamed:")
            ]

    if df_clean.empty:
        print(f" Warning: No valid records parsed from {file_name}. Skipping insert.")
        return

    df_clean.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df_clean)} rows into Fact_EquipmentState.")

def process_and_load_sap(file_path, file_name):
    """Cleans both transactional goods movement logs and production column sheets into SSMS."""
    print(f"Processing SAP File: {file_name}...")

    xls = pd.ExcelFile(file_path)
    target_sheet = next(
        (s for s in xls.sheet_names if any(k in s.lower() for k in ["raw", "data", "list", "detail", "pv", "volume"])),
        xls.sheet_names[0]
    )

    df = pd.read_excel(file_path, sheet_name=target_sheet)
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', ' ')
    cols_upper = [str(c).upper() for c in df.columns]

    df_clean = pd.DataFrame()

    def find_col(keywords):
        for col in df.columns:
            col_str = str(col).upper().strip()
            for kw in keywords:
                if kw == col_str or kw in col_str:
                    return col
        return None

    # Check for Matrix/Summary Production Volume Layout
    has_matrix_cols = any(
        k in cols_upper for k in ["MATERIAL CODE", "SUM.TOTAL", "[WT]SUM.TOTAL", "TOTAL", "PRODUCTION"]) or \
                      any("PV" in str(s).upper() for s in xls.sheet_names)

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
                parent_rows[pcs_col].astype(str).str.replace('-', '0').str.replace(',', ''), errors="coerce"
            )
            df_clean["UnitOfEntry"] = "PCS"
            df_clean["PostingDate"] = pd.Timestamp.now().date()

    elif has_matrix_cols and find_col(["MATERIAL", "CODE", "PRODUCT"]):
        print(" -> Detected Production Volume / Summary Matrix Layout")
        mat_col = find_col(["MATERIAL CODE", "MATERIAL", "PRODUCT", "ITEM"])
        qty_col = find_col(["SUM.TOTAL", "SUM.GR", "[WT]SUM.TOTAL", "TOTAL", "QTY", "QUANTITY"])

        if mat_col:
            df_clean["Plant"] = "P313"
            df_clean["StorageLocation"] = "PROD"
            df_clean["MovementType"] = 101
            df_clean["MaterialCode"] = df[mat_col].astype(str).str.strip()
            df_clean["MaterialDescription"] = "Production Volume Output"
            df_clean["Quantity"] = pd.to_numeric(df[qty_col], errors="coerce") if qty_col else 0
            df_clean["UnitOfEntry"] = "PCS"
            df_clean["PostingDate"] = pd.Timestamp.now().date()

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

        # Positional fallbacks if columns are not named explicitly
        if not col_mat and len(df.columns) >= 7:
            col_mat = df.columns[6]
        if not col_desc and len(df.columns) >= 9:
            col_desc = df.columns[8]
        if not col_qty and len(df.columns) >= 14:
            col_qty = df.columns[13]

        df_clean["Plant"] = df[col_plant].astype(str).str.strip() if col_plant else "P313"
        df_clean["StorageLocation"] = df[col_sloc].astype(str).str.strip() if col_sloc else "PROD"
        df_clean["MovementType"] = df[col_mvt] if col_mvt else 101
        df_clean["MaterialCode"] = df[col_mat].astype(str).str.strip() if col_mat else None
        df_clean["MaterialDescription"] = df[col_desc].astype(str).str.strip() if col_desc else "SAP Material"
        df_clean["Quantity"] = pd.to_numeric(df[col_qty], errors="coerce") if col_qty else 0
        df_clean["UnitOfEntry"] = df[col_uom].astype(str).str.strip() if col_uom else "PCS"

        if col_date:
            df_clean["PostingDate"] = pd.to_datetime(df[col_date], errors="coerce").dt.date
        else:
            df_clean["PostingDate"] = pd.Timestamp.now().date()

        if col_doc:
            df_clean["MaterialDocument"] = df[col_doc].astype(str).str.strip()

    # Guarantee required non-nullable columns have defaults
    df_clean["Plant"] = df_clean["Plant"].fillna("P313")
    df_clean["StorageLocation"] = df_clean["StorageLocation"].fillna("PROD")
    df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce").fillna(0)

    # Clean empty records
    df_clean = df_clean[df_clean["Quantity"] > 0].copy()
    df_clean.dropna(subset=["MaterialCode"], inplace=True)
    df_clean = df_clean[df_clean["MaterialCode"].astype(str).str.strip() != "nan"]
    df_clean["SourceFileName"] = file_name

    if df_clean.empty:
        print(f" Warning: No valid rows processed from {file_name}. Skipping insert.")
        return

    df_clean.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df_clean)} rows into Fact_SAP_MaterialMovement.")

def main():
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Directory '{RAW_DATA_DIR}' not found. Please create it and add your Excel files.")
        return

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(('.xlsx', '.xls', '.XLSX', '.XLS'))]
    if not files:
        print(f"No Excel files found in '{RAW_DATA_DIR}'. Drop your files there first.")
        return

    for file_name in files:
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        if "SAP" in file_name.upper():
            process_and_load_sap(file_path, file_name)
        else:
            process_and_load_mes(file_path, file_name)

if __name__ == "__main__":
    main()