import pandas as pd
from config import get_db_engine
from ingest_mes import process_mes_file
from ingest_sap import process_sap_file, process_production_file

def load_mes_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_mes_file(file_path)
    
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    print(f"🧹 MES File: Removed {duplicates_removed} duplicate rows (Kept {len(df)} rows).")
    
    df["SourceFileName"] = file_name
    df.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_EquipmentState.")

def load_sap_production_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_production_file(file_path)
    
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    print(f"🧹 SAP Production File: Removed {duplicates_removed} duplicate rows (Kept {len(df)} rows).")
    
    df["SourceFileName"] = file_name
    df.to_sql("Fact_SAP_ProductionVolume", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_SAP_ProductionVolume.")

def load_sap_movement_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_sap_file(file_path)
    
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    print(f"🧹 SAP Material Movement File: Removed {duplicates_removed} duplicate rows (Kept {len(df)} rows).")
    
    df["SourceFileName"] = file_name
    df.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_SAP_MaterialMovement.")