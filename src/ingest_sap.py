"""
SAP Data Ingestion Module.
Handles SAP Production Volume (RD source), Material Movement/Consumption logs,
and KPI 2026 Reference normalization. Implements ZBOM flagging and yield/MW formulas.
"""

import pandas as pd

# Standardized column mapping for Material Consumption logs
column_mapping = {
    "Plant": "Plant",
    "Storage location": "StorageLocation",
    "Movement type": "MovementType",
    "Movement Type Text": "MovementTypeText",
    "Bill of Lading": "BillOfLading",
    "Receiving plant": "ReceivingPlant",
    "Receiving stor. loc.": "ReceivingStorageLocation",
    "Material": "MaterialCode",
    "Goods Recipient": "GoodsRecipient",
    "Material Description": "MaterialDescription",
    "Document Header Text": "DocumentHeaderText",
    "Batch": "Batch",
    "Purchase order": "PurchaseOrder",
    "Quantity": "Quantity",
    "Unit of Entry": "UnitOfEntry",
    "Material Document": "MaterialDocument",
    "Posting Date": "PostingDate",
    "Document Date": "DocumentDate",
    "Entry Date": "EntryDate",
    "Time of Entry": "TimeOfEntry",
    "User Name": "UserName",
    "Text": "Text",
    "Supplier": "Supplier",
    "Amt.in Loc.Cur.": "AmountLocalCurrency",
    "Currency": "Currency",
    "Order": "Order",
    "Reservation": "Reservation",
    "Reference": "Reference",
    "Item": "Item",
    "Entered On(EST)": "EnteredOnEST",
    "Time of Entry(EST)": "TimeOfEntryEST",
    "Debit/Credit ind": "DebitCreditIndicator",
    "Cost Center": "CostCenter",
}

def clean_missing_values(df):
    """Replaces all NaN/NaT dataframe values with None for safe SQL database compatibility."""
    return df.where(pd.notnull(df), None)

def process_sap_rd_production_file(file_path):
    """
    Ingests SAP RD (0801) as the primary detailed production source.
    Flags ZBOM records (#VALUE!), calculates Production Volume (MW), and maps Qgrades.
    """
    xls = pd.ExcelFile(file_path)
    sheet_name = "2) SAP RD (0801)" if "2) SAP RD (0801)" in xls.sheet_names else xls.sheet_names[0]
    
    df = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Flag ZBOM / #VALUE! records prior to cleaning (retained in raw layer, excluded from KPI calculations)
    df["IsZBOM"] = 0
    if "Material" in df.columns:
        df["IsZBOM"] = df["Material"].astype(str).str.contains("#VALUE!", regex=False).astype(int)
    if "PCS" in df.columns:
        df["IsZBOM"] = df["IsZBOM"] | df["PCS"].astype(str).str.contains("#VALUE!", regex=False).astype(int)

    # Standardize column names
    clean_cols = {col: str(col).strip().replace("[", "").replace("]", "").replace(" ", "").replace(".", "_") for col in df.columns}
    df_clean = df.rename(columns=clean_cols).copy()

    # Map core sponsor fields safely as Series
    df_clean["MaterialCode"] = df_clean["Material"].astype(str).str.strip() if "Material" in df_clean.columns else None
    df_clean["MaterialDescription"] = df_clean["MaterialDescription"].astype(str).str.strip() if "MaterialDescription" in df_clean.columns else None
    
    eff_series = df_clean["Efficiency_WT_"] if "Efficiency_WT_" in df_clean.columns else pd.Series(0.0, index=df_clean.index)
    gr_series = df_clean["GR"] if "GR" in df_clean.columns else pd.Series(0.0, index=df_clean.index)

    df_clean["Efficiency_WT"] = pd.to_numeric(eff_series, errors="coerce").fillna(0.0)
    df_clean["GR_Qty"] = pd.to_numeric(gr_series, errors="coerce").fillna(0.0)
    df_clean["Qgrade"] = df_clean.get("Qgrade", pd.Series("Unmapped", index=df_clean.index)).astype(str).str.strip()
    
    def categorize_grade(grade):
        """Maps module grades to Good, Defect, or Other / Unmapped."""
        if grade in ["G01", "G02"]:
            return "Good"
        elif grade == "C":
            return "Defect"
        else:
            return "Other / Unmapped"

    df_clean["GradeCategory"] = df_clean["Qgrade"].apply(categorize_grade)

    # Sponsor Production Volume Formula: MW = Efficiency (WT) * GR / 1,000,000 (rounded to 2 decimal places)
    df_clean["ProductionVolume_MW"] = (df_clean["Efficiency_WT"] * df_clean["GR_Qty"]) / 1000000.0
    df_clean["ProductionVolume_MW"] = df_clean["ProductionVolume_MW"].round(2)

    return clean_missing_values(df_clean)

def process_sap_material_movement_file(file_path):
    """Ingests raw SAP material consumption and goods movement logs, preserving all duplicate records."""
    df = pd.read_excel(file_path)

    rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
    df_clean = df.rename(columns=rename_dict).copy()

    date_cols = ["PostingDate", "DocumentDate", "EntryDate", "EnteredOnEST"]
    for col in date_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce").dt.date

    numeric_cols = ["Quantity", "MovementType", "AmountLocalCurrency", "Item", "Reservation", "Reference"]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    if "MaterialDocument" in df_clean.columns:
        df_clean["MaterialDocument"] = pd.to_numeric(df_clean["MaterialDocument"], errors="coerce").astype("Int64")

    return clean_missing_values(df_clean)

def process_kpi_2026_file(file_path):
    """
    Normalizes KPI 2026 reference data into the sponsor-recommended schema:
    Year | Month | Fab | Site | ProductName | KPI | Unit | Value.
    Excludes complex Cell Loss calculations as instructed.
    """
    xls = pd.ExcelFile(file_path)
    records = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        if df.empty:
            continue
        
        for idx, row in df.iterrows():
            fab = row.get("Fab", "Qcells")
            site = row.get("Site", "Dalton")
            product = row.get("Product Name", row.get("Product", "General"))
            year = row.get("Year", 2026)
            month = row.get("Month", 1)

            for col in df.columns:
                if col in ["Fab", "Site", "Product Name", "Product", "Year", "Month"]:
                    continue
                
                # Exclude Cell Loss per sponsor instructions
                if "cell loss" in str(col).lower():
                    continue

                val = row[col]
                if pd.notna(val):
                    unit = "MW" if "MW" in str(col) else ("%" if "%" in str(col) or "Yield" in str(col) else "Units")
                    try:
                        clean_val = round(float(val), 2)
                        records.append({
                            "Year": int(year),
                            "Month": int(month),
                            "Fab": str(fab).strip(),
                            "Site": str(site).strip(),
                            "ProductName": str(product).strip(),
                            "KPI": str(col).strip(),
                            "Unit": unit,
                            "Value": clean_val
                        })
                    except (ValueError, TypeError):
                        continue

    df_normalized = pd.DataFrame(records)
    return clean_missing_values(df_normalized) if not df_normalized.empty else df_normalized