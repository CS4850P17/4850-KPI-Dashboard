import os
from import_to_sql import (
    load_mes_to_sql, 
    load_sap_production_to_sql, 
    load_sap_movement_to_sql
)

RAW_DATA_DIR = os.path.join("data", "raw")

def route_and_load_file(file_path, file_name):
    """Routes each raw Excel file to its corresponding database loader based on naming keywords."""
    name_upper = file_name.upper()
    
    if any(keyword in name_upper for keyword in ["MES", "TABBER", "EQP"]):
        load_mes_to_sql(file_path, file_name)
    elif any(keyword in name_upper for keyword in ["PROD", "VOLUME", "PV"]):
        load_sap_production_to_sql(file_path, file_name)
    elif any(keyword in name_upper for keyword in ["SAP", "MOVEMENT", "MATERIAL"]):
        load_sap_movement_to_sql(file_path, file_name)
    else:
        print(f"⚠️ Unrecognized file pattern for '{file_name}'. Skipping.")

def run_pipeline():
    """Scans the raw data directory and executes the automated ingestion pipeline."""
    if not os.path.exists(RAW_DATA_DIR):
        print(f"❌ Error: Directory '{RAW_DATA_DIR}' not found. Please create it and add your Excel files.")
        return

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith(('.xlsx', '.xls'))]
    if not files:
        print(f"⚠️ No Excel files found in '{RAW_DATA_DIR}'.")
        return

    print(f"📁 Found {len(files)} file(s) to process.")
    
    for file_name in files:
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        print(f"\n▶ Processing file: {file_name}")
        route_and_load_file(file_path, file_name)

if __name__ == "__main__":
    print("=== Starting KPI Dashboard Pipeline ===")
    run_pipeline()
    print("\n=== Pipeline Execution Complete ===")