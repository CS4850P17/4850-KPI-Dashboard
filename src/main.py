#all the imports used
import numpy as np
import pandas as pd
import os
from config import get_db_engine
from ingest_mes import process_mes_file
from ingest_sap import process_sap_file

def run_pipeline():
  engine = get_db_engine()
  raw_dir = os.path.join("data", "raw")

  print("Starting pipeline execution...")

  for file_name in os.listdir(raw_dir):
    file_path = os.path.join(raw_dir, file_name)

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


let preprocessing():
  #load the file
  #do what needs to be done on the file like filling the nulls/blanks if necessary.
  #save the file to be used later in PowerBI as a json or some other data file type






if __name__ = "__main__":
  preprocessing()
  run_pipeline()
