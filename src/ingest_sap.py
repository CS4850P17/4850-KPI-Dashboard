import pandas as pd

column_mapping = {
        "Plant": "Plant",
        "Storage location": "StorageLocation",
        "Movement type": "MovementType",
        "Material": "MaterialCode",
        "Material Description": "MaterialDescription",
        "Batch": "Batch",
        "Quantity": "Quantity",
        "Unit of Entry": "UnitOfEntry",
        "Posting Date": "PostingDate",
        "Material Document": "MaterialDocument"
    }

def process_sap_file(file_path):
    """
    Reads raw SAP goods movement exports and cleans columns for Fact_SAP_MaterialMovement.
    """
    df = pd.read_excel(file_path)
    
    # Map raw SAP header names to database fields

    
    df_clean = df[list(column_mapping.keys())].rename(columns=column_mapping)
    
    # Data type conversions
    df_clean["PostingDate"] = pd.to_datetime(df_clean["PostingDate"]).dt.date
    df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce")
    df_clean["MovementType"] = pd.to_numeric(df_clean["MovementType"], errors="coerce")
    
    return df_clean
