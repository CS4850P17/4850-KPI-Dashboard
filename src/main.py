"""
Main Pipeline Execution Script.
Scans the raw data directory, routes files dynamically based on sponsor naming conventions,
and loads them into the database.
"""

    # MES file ingestion
    if "MES" in file_name.upper() or "TABBER" in file_name.upper():
      print(f"Processing MES file: {file_name}")
      df_mes = process_mes_file(file_path)
      df_mes.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
      print(f"Successfully loaded {len(df_mes)} rows into Fact_EquipmentState.")

    # SAP file ingestion
    elif "SAP" in file_name.upper() or "311" in file_name:
      print(f"Processing SAP file: {file_name}")
      df_sap = process_sap_file(file_path)
      df_sap.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
      print(f"Successfully loaded {len(df_sap)} rows into Fact_SAP_MaterialMovement.")



  #load the file
  #do what needs to be done on the file like filling the nulls/blanks if necessary.
  #save the file to be used later in PowerBI as a json or some other data file type

RAW_DATA_DIR = os.path.join("data", "raw")


def route_and_load_file(file_path: str, file_name: str):
    """Routes files to the appropriate ingestion function according to sponsor rules."""
    name_upper = file_name.upper()

    if any(k in name_upper for k in ["MES", "TABBER", "EQP", "OPERATION"]):
        load_mes_to_sql(file_path, file_name)
    elif any(k in name_upper for k in ["KPI", "2026", "REFERENCE"]):
        load_kpi_reference_to_sql(file_path, file_name)
    elif any(k in name_upper for k in ["PROD", "VOLUME", "PV", "RD"]):
        load_sap_production_to_sql(file_path, file_name)
    elif any(k in name_upper for k in ["SAP", "MOVEMENT", "MATERIAL", "CONSUMPTION"]):
        load_sap_movement_to_sql(file_path, file_name)
    else:
        print(f"⚠️ Unrecognized file pattern for '{file_name}'. Skipping.")


if __name__ == "__main__":
    run_pipeline()
