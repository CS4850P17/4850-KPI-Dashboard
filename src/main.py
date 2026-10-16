import os
from import_to_sql import load_mes_to_sql, load_sap_production_to_sql, load_sap_movement_to_sql

RAW_DATA_DIR = os.path.join("data", "raw")

def run_pipeline():
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Directory '{RAW_DATA_DIR}' not found. Please create it and add your Excel files.")
        return

    files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith(('.xlsx', '.xls'))]
    if not files:
        print(f"No Excel files found in '{RAW_DATA_DIR}'.")
        return

    for file_name in files:
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        print(f"\nProcessing file: {file_name}")
        
        upper_name = file_name.upper()
        if "MES" in upper_name or "TABBER" in upper_name or "EQP" in upper_name:
            load_mes_to_sql(file_path, file_name)
        elif "PROD" in upper_name or "VOLUME" in upper_name or "PV" in upper_name:
            load_sap_production_to_sql(file_path, file_name)
        elif "SAP" in upper_name or "MOVEMENT" in upper_name or "MATERIAL" in upper_name:
            load_sap_movement_to_sql(file_path, file_name)
        else:
            print(f"⚠️ Unrecognized file pattern for: {file_name}. Skipping.")

if __name__ == "__main__":
    print("Starting KPI Dashboard Pipeline...")
    run_pipeline()
    print("Pipeline execution complete!")