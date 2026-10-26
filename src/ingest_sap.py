import pandas as pd
import numpy as np

# Standardized column mapping for SQL compatibility
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
    """Replaces all NaN/NaT values with None for safe SQL database compatibility."""
    return df.where(pd.notnull(df), None)

def process_production_file(file_path):
    """Reads and cleans SAP Production Volume reports while retaining all data."""
    df = pd.read_excel(file_path, header=None)
    header_row = None
    
    # Locate dynamic header row
    for i in range(min(20, len(df))):
        row_vals = [str(v).strip().casefold() for v in df.iloc[i].tolist()]
        if "row labels" in row_vals and "mw" in row_vals and "pcs" in row_vals:
            header_row = i
            break
            
    if header_row is None:
        raise ValueError("Header row containing 'Row Labels', 'MW', and 'PCS' not found.")
        
    df.columns = df.iloc[header_row].astype(str).str.strip()
    df_clean = df.iloc[header_row + 1:].copy()
    
    if "Row Labels" in df_clean.columns:
        df_clean = df_clean.rename(columns={"Row Labels": "RowLabels"})
        
    # Enforce numeric types safely
    for col in ["MW", "PCS"]:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            
    return clean_missing_values(df_clean).reset_index(drop=True)

def process_sap_file(file_path):
    """Ingests raw SAP material data, preserves duplicates/extra columns, and standardizes types."""
    df = pd.read_excel(file_path)

    # Rename mapped columns while keeping any extra unmapped columns intact
    rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
    df_clean = df.rename(columns=rename_dict).copy()

    # Standardize Date fields
    date_cols = ["PostingDate", "DocumentDate", "EntryDate", "EnteredOnEST"]
    for col in date_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce").dt.date

    # Standardize Numeric fields
    numeric_cols = ["Quantity", "MovementType", "AmountLocalCurrency", "Item", "Reservation", "Reference"]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Handle nullable integer formatting for Material Document
    if "MaterialDocument" in df_clean.columns:
        df_clean["MaterialDocument"] = pd.to_numeric(df_clean["MaterialDocument"], errors="coerce").astype("Int64")

    # Final sanitization pass for SQL compatibility (retains all rows and duplicates)
    return clean_missing_values(df_clean)