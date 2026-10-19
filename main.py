# all the imports used
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

            # Use the new function for Equipment Operation Rate data
            if "EQP OPERATION RATE" in file_name.upper():
                df_mes = process_equipment_data(file_path)
            else:
                df_mes = process_mes_file(file_path)

            if df_mes.empty:
                print(f"No valid MES records to load from {file_name}.")
                continue

            df_mes.to_sql("Fact_EquipmentState", con=engine, if_exists="append", index=False)
            print(f"Successfully loaded {len(df_mes)} rows into Fact_EquipmentState.")

        # SAP file ingestion
        elif "SAP" in file_name.upper() or "311" in file_name:
            print(f"Processing SAP file: {file_name}")
            df_sap = process_sap_file(file_path)
            df_sap.to_sql("Fact_SAP_MaterialMovement", con=engine, if_exists="append", index=False)
            print(f"Successfully loaded {len(df_sap)} rows into Fact_SAP_MaterialMovement.")


def preprocessing():
    # load the file
    # do what needs to be done on the file like filling the nulls/blanks if necessary.
    # save the file to be used later in PowerBI as a json or some other data file type
    print("")


def process_equipment_data(file_path):
    """Clean all MES equipment sheets and prepare status records for SQL Server."""

    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    equipment_sheets = ["1) Tabber", "2) Front End", "3) Back End"]
    all_equipment = []
    quality_issues = []

    # 1. Read each manufacturing-area worksheet

    for sheet_name in equipment_sheets:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.columns = df.columns.astype(str).str.strip()

        if "EQUIPMENT" not in df.columns or "RUN" not in df.columns:
            raise ValueError(f"Required columns missing in {sheet_name}")

        df["EQUIPMENT"] = df["EQUIPMENT"].astype("string").str.strip()
        df = df.dropna(subset=["EQUIPMENT"])
        df = df[df["EQUIPMENT"] != ""].copy()

        status_columns = [col for col in df.columns if col != "EQUIPMENT"]
        df[status_columns] = df[status_columns].apply(pd.to_numeric, errors="coerce")
        df["Area"] = sheet_name.split(") ", 1)[1]

        # 2. Validate missing, invalid and zero percentages

        for _, row in df.iterrows():
            values = row[status_columns]
            reasons = []

            if values.isna().any():
                reasons.append("Missing or nonnumeric percentage")

            if ((values < 0) | (values > 100)).any():
                reasons.append("Percentage outside 0-100")

            if values.notna().all() and (values == 0).all():
                reasons.append("All equipment status values are zero")

            if reasons:
                quality_issues.append({
                    "Area": row["Area"],
                    "EquipmentName": row["EQUIPMENT"],
                    "Issue": "; ".join(reasons)
                })
            else:
                all_equipment.append(row.to_dict())

    if not all_equipment:
        raise ValueError("No valid equipment records found in the workbook")

    # 3. Calculate equipment performance

    clean = pd.DataFrame(all_equipment)

    kpi = clean[["Area", "EQUIPMENT", "RUN"]].copy()
    kpi = kpi.rename(columns={
        "EQUIPMENT": "EquipmentName",
        "RUN": "RunPercentage"
    })

    status_columns = [
        c for c in clean.columns
        if c not in ["Area", "EQUIPMENT"]
    ]

    kpi["NonRunPercentage"] = clean[
        [c for c in status_columns if c != "RUN"]
    ].sum(axis=1).to_numpy()

    # 4. Generate manufacturing-area summary

    area_summary = kpi.groupby("Area", as_index=False).agg(
        EquipmentCount=("EquipmentName", "count"),
        AverageRunPercentage=("RunPercentage", "mean"),
        AverageNonRunPercentage=("NonRunPercentage", "mean")
    )

    # 5. Prepare equipment records for SQL Server

    sql_records = clean.melt(
        id_vars=["Area", "EQUIPMENT"],
        value_vars=status_columns,
        var_name="Category",
        value_name="TimePercentage"
    ).rename(columns={
        "EQUIPMENT": "EquipmentName"
    })

    sql_records = sql_records[
        ["Category", "EquipmentName", "TimePercentage"]
    ]

    # 6. Save processed data

    sql_records.to_csv(
        os.path.join(processed_dir, "mes_equipment_status.csv"),
        index=False
    )

    kpi.to_csv(
        os.path.join(processed_dir, "mes_equipment_kpi.csv"),
        index=False
    )

    area_summary.to_csv(
        os.path.join(processed_dir, "mes_area_summary.csv"),
        index=False
    )

    pd.DataFrame(
        quality_issues,
        columns=["Area", "EquipmentName", "Issue"]
    ).to_csv(
        os.path.join(processed_dir, "mes_data_quality.csv"),
        index=False
    )

    # 7. Display processing results

    print(f"Accepted equipment: {len(kpi)}")
    print(f"Equipment needing review: {len(quality_issues)}")
    print(f"Prepared SQL status rows: {len(sql_records)}")

    return sql_records


if __name__ == "__main__":
    preprocessing()
    run_pipeline()
