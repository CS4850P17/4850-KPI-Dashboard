import pandas as pd

# Raw SAP header -> clean column name
# (Purchase order, Bill of Lading, Supplier, Order, Cost Center are left out, so they are dropped)
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

def process_sap_file(file_path):
    """
    Reads the raw SAP material consumption export, removes duplicates,
    drops unneeded columns, and standardizes names and data types.
    """
    df = pd.read_excel(file_path)

    # Drop exact duplicate rows (done on the full raw row, as in your original code)
    df = df.drop_duplicates()

    # Keep only mapped columns and rename them
    df_clean = df[list(column_mapping.keys())].rename(columns=column_mapping)

    # Data type conversions
    for col in ["PostingDate", "DocumentDate", "EntryDate", "EnteredOnEST"]:
        df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce").dt.date

    for col in ["Quantity", "MovementType", "AmountLocalCurrency",
                "Item", "Reservation", "Reference"]:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Material Document is an ID, so keep it as an integer (not 4.9e+09 float)
    df_clean["MaterialDocument"] = pd.to_numeric(
        df_clean["MaterialDocument"], errors="coerce"
    ).astype("Int64")

    return df_clean


df = process_sap_file("input_files/3_SAP_Material Consumption Raw Data.XLSX")
print(df)
