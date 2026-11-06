"""
Database Import and Loading Module.
Manages database loading routines for MES equipment data, SAP production volume, 
SAP material movements, and normalized KPI 2026 reference tables.
"""

import pandas as pd
from config import get_db_engine
from ingest_mes import process_mes_file
from ingest_sap import (
    process_kpi_2026_file,
    process_sap_material_movement_file,
    process_sap_rd_production_file,
)


def count_and_report_duplicates(df: pd.DataFrame, dataset_name: str):
    """Counts duplicate rows without removing them to preserve raw-data fidelity."""
    duplicate_count = df.duplicated().sum()
    print(f"📊 {dataset_name}: Found {duplicate_count} duplicate rows (All retained).")


def load_mes_to_sql(file_path: str, file_name: str):
    engine = get_db_engine()
    df = process_mes_file(file_path)
    if df.empty:
        return
    count_and_report_duplicates(df, "MES Equipment Data")
    df["SourceFileName"] = file_name
    df.to_sql("Fact_EquipmentState", con=engine, if_exists="replace", index=False)
    print(f"Successfully loaded {len(df)} rows into Fact_EquipmentState.")


def load_sap_production_to_sql(file_path: str, file_name: str):
    engine = get_db_engine()
    df_rd = process_sap_rd_production_file(file_path)
    if df_rd.empty:
        return
    count_and_report_duplicates(df_rd, "SAP RD Production Volume Data")
    df_rd["SourceFileName"] = file_name
    df_rd.to_sql("Fact_SAP_ProductionVolume", con=engine, if_exists="replace", index=False)
    print(f"Successfully loaded {len(df_rd)} rows into Fact_SAP_ProductionVolume (Primary RD Source).")


def load_sap_movement_to_sql(file_path: str, file_name: str):
    engine = get_db_engine()
    df_sap = process_sap_material_movement_file(file_path)
    if df_sap.empty:
        return
    count_and_report_duplicates(df_sap, "SAP Material Movement Data")
    df_sap["SourceFileName"] = file_name
    df_sap.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="replace", index=False)
    print(f"Successfully loaded {len(df_sap)} rows into Fact_SAP_MaterialMovement.")


def load_kpi_reference_to_sql(file_path: str, file_name: str):
    engine = get_db_engine()
    df_kpi = process_kpi_2026_file(file_path)
    if df_kpi.empty:
        return
    count_and_report_duplicates(df_kpi, "KPI 2026 Reference Data")
    df_kpi["SourceFileName"] = file_name
    df_kpi.to_sql("Fact_KPI_Reference", con=engine, if_exists="replace", index=False)
    print(f"Successfully loaded {len(df_kpi)} rows into Fact_KPI_Reference.")
