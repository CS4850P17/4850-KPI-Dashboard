import pandas as pd

column_mapping = {
    "Plant": "Plant",
    "Storage location": "StorageLocation",
    "Movement type": "MovementType",
    "Movement Type Text": "MovementTypeText",
    "Receiving plant": "ReceivingPlant",
    "Receiving stor. loc.": "ReceivingStorageLocation",
    "Material": "MaterialCode",
    "Goods Recipient": "GoodsRecipient",
    "Material Description": "MaterialDescription",
    "Document Header Text": "DocumentHeaderText",
    "Batch": "Batch",
    "Quantity": "Quantity",
    "Unit of Entry": "UnitOfEntry",
    "Material Document": "MaterialDocument",
    "Posting Date": "PostingDate",
    "Document Date": "DocumentDate",
    "Entry Date": "EntryDate",
    "Time of Entry": "TimeOfEntry",
    "User Name": "UserName",
    "Text": "Text",
    "Amt.in Loc.Cur.": "AmountLocalCurrency",
    "Currency": "Currency",
    "Reservation": "Reservation",
    "Reference": "Reference",
    "Item": "Item",
    "Entered On(EST)": "EnteredOnEST",
    "Time of Entry(EST)": "TimeOfEntryEST",
    "Debit/Credit ind": "DebitCreditIndicator",
}

def process_production_file(file_path):
    """Reads the SAP Production Volume report and keeps all columns."""
    df = pd.read_excel(file_path, header=None)
    header_row = None
    for i in range(min(20, len(df))):
        row_values = [str(value).strip().casefold() for value in df.iloc[i].tolist()]
        if "row labels" in row_values and "mw" in row_values and "pcs" in row_values:
            header_row = i
            break
            
    if header_row is None:
        raise ValueError("Could not find the header row containing 'Row Labels', 'MW', and 'PCS'.")
        
    df.columns = df.iloc[header_row].astype(str).str.strip()
    df_clean = df.iloc[header_row + 1:].copy()
    
    if "Row Labels" in df_clean.columns:
        df_clean = df_clean.rename(columns={"Row Labels": "RowLabels"})
        
    for col in ["MW", "PCS"]:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            
    return df_clean.reset_index(drop=True)

def process_sap_file(file_path):
    """Reads raw SAP material consumption, renames mapped columns, but keeps all extra columns."""
    df = pd.read_excel(file_path)

    # Rename only the columns that exist in our mapping dictionary, keep the rest
    rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
    df_clean = df.rename(columns=rename_dict).copy()

    # Data type conversions for date fields if present
    for col in ["PostingDate", "DocumentDate", "EntryDate", "EnteredOnEST"]:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce").dt.date

    # Data type conversions for numeric fields if present
    numeric_cols = [
        "Quantity", "MovementType", "AmountLocalCurrency", 
        "Item", "Reservation", "Reference"
    ]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    if "MaterialDocument" in df_clean.columns:
        df_clean["MaterialDocument"] = pd.to_numeric(
            df_clean["MaterialDocument"], errors="coerce"
        ).astype("Int64")

    return df_clean