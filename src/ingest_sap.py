import pandas as pd

# Comprehensive raw SAP header -> clean column name mapping for material consumption
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
    """
    Reads the SAP Production Volume report with extra title/header rows.
    Expected actual headers: Row Labels, MW, PCS.
    """
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
    df = df.iloc[header_row + 1:].copy()
    
    # Check if required columns exist
    required_columns = ["Row Labels", "MW", "PCS"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing production column: {col}")
            
    df_clean = df[required_columns].copy()
    df_clean = df_clean.rename(columns={"Row Labels": "RowLabels"})
    df_clean = df_clean.dropna(subset=["RowLabels"])
    
    for col in ["MW", "PCS"]:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        
    return df_clean.drop_duplicates().reset_index(drop=True)

def process_sap_file(file_path):
    """
    Reads the raw SAP material consumption export, removes duplicates,
    drops unneeded columns, and standardizes names and data types.
    """
    df = pd.read_excel(file_path)

    # Drop exact duplicate rows
    df = df.drop_duplicates()

    # Filter mapping keys that actually exist in the uploaded file to avoid KeyErrors
    valid_cols = [col for col in column_mapping.keys() if col in df.columns]
    
    df_clean = df[valid_cols].copy()
    df_clean = df_clean.rename(columns={k: column_mapping[k] for k in valid_cols})

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

    # Material Document formatting as integer identifier
    if "MaterialDocument" in df_clean.columns:
        df_clean["MaterialDocument"] = pd.to_numeric(
            df_clean["MaterialDocument"], errors="coerce"
        ).astype("Int64")

    return df_clean