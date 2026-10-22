import pandas as pd
from config import get_db_engine
from ingest_mes import process_mes_file
from ingest_sap import process_sap_file, process_production_file

def count_and_report_duplicates(df: pd.DataFrame, dataset_name: str):
    """Counts duplicate rows without removing them."""
    duplicate_count = df.duplicated().sum()
    print(f"📊 {dataset_name}: Found {duplicate_count} duplicate rows (All retained).")

def load_mes_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_mes_file(file_path)
    
    count_and_report_duplicates(df, "MES Equipment Data")
    
    df["SourceFileName"] = file_name
    df.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_EquipmentState.")

def load_sap_production_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_production_file(file_path)
    
    count_and_report_duplicates(df, "SAP Production Volume Data")
    
    df["SourceFileName"] = file_name
    df.to_sql("Fact_SAP_ProductionVolume", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_SAP_ProductionVolume.")

def load_sap_movement_to_sql(file_path, file_name):
    engine = get_db_engine()
    df = process_sap_file(file_path)
    
    count_and_report_duplicates(df, "SAP Material Movement Data")
    
    df["SourceFileName"] = file_name
    df.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_SAP_MaterialMovement.")