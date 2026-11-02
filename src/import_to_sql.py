import pandas as pd
from config import get_db_engine
from ingest_mes import process_mes_file
from ingest_sap import process_sap_file, process_production_file, process_sap_rd_file

def count_and_report_duplicates(df: pd.DataFrame, dataset_name: str):
    """Counts duplicate rows without removing them."""
    if df is not None and not df.empty:
        duplicate_count = df.duplicated().sum()
        print(f"📊 {dataset_name}: Found {duplicate_count} duplicate rows (All retained).")

def load_mes_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_mes_file(file_path)

    if df is not None and not df.empty:
        count_and_report_duplicates(df, "MES Equipment Data (All Sheets)")
        df["SourceFileName"] = file_name
        df.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
        print(f"Successfully loaded {len(df)} rows into Fact_EquipmentState.")
    else:
        print(f" ⚠️ Warning: Skipping insert for {file_name} because parsed dataset is empty.")

def load_sap_production_to_sql(file_path, file_name):
    engine = get_db_engine()
    
    # 1. Load SAP Production Volume (Sheet 1)
    df_pv = process_production_file(file_path)
    if df_pv is not None and not df_pv.empty:
        count_and_report_duplicates(df_pv, "SAP Production Volume Data")
        df_pv["SourceFileName"] = file_name
        df_pv.to_sql("Fact_SAP_ProductionVolume", con=engine, if_exists="append", index=False)
        print(f"Successfully loaded {len(df_pv)} rows into Fact_SAP_ProductionVolume.")
    else: 
        print(f"⚠️ Warning: Skipping Production Volume insert for {file_name} (dataset empty).")
    
    # 2. Load SAP Raw Data / Stock Status (Sheet 2)
    df_rd = process_sap_rd_file(file_path)
    if df_rd is not None and not df_rd.empty:
        count_and_report_duplicates(df_rd, "SAP Raw Data / Stock Status")
        df_rd["SourceFileName"] = file_name
        df_rd.to_sql("Fact_SAP_RawData", con=engine, if_exists="append", index=False)
        print(f"Successfully loaded {len(df_rd)} rows into Fact_SAP_RawData.")

def load_sap_movement_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_sap_file(file_path)

    if df is not None and not df.empty:
        count_and_report_duplicates(df, "SAP Material Movement Data")
        df["SourceFileName"] = file_name
        df.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
        print(f"Successfully loaded {len(df)} rows into Fact_SAP_MaterialMovement.")
    else: 
        print(f"⚠️ Warning: Skipping insert for {file_name} because parsed dataset is empty.")
