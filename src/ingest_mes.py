"""
MES Data Ingestion Module.
Processes MES Equipment Operation Rate files across manufacturing areas 
(Tabber, Front End, Back End), handling blank status cells and preserving raw data fidelity.
"""

import pandas as pd

def process_mes_file(file_path):
    """
    Reads all manufacturing worksheets from the MES workbook, melts status matrices,
    flags completely blank equipment columns as N/A, and cleans numeric percentages.
    """
    xls = pd.ExcelFile(file_path)
    all_sheets_data = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        if df.empty:
            continue
        
        category_col = df.columns[0]
        
        # Melt wide status matrix into long format for database loading
        df_melted = pd.melt(
            df, 
            id_vars=[category_col], 
            var_name="EquipmentName", 
            value_name="TimePercentage"
        )
        df_melted.rename(columns={category_col: "Category"}, inplace=True)
        df_melted["SheetName"] = sheet_name.strip()
        
        # Identify completely blank equipment columns (Treat as N/A / No Available Data)
        blank_equipments = df_melted.groupby("EquipmentName")["TimePercentage"].apply(lambda x: x.isna().all())
        blank_eq_names = set(blank_equipments[blank_equipments].index)

        # Standardize string formatting
        df_melted["EquipmentName"] = df_melted["EquipmentName"].astype(str).str.strip()
        df_melted["Category"] = df_melted["Category"].astype(str).str.strip()
        
        # Filter out summary / average header rows
        exclude_keywords = ["average", "total", "sum", "mean"]
        df_melted = df_melted[
            ~df_melted["EquipmentName"].str.lower().isin(exclude_keywords)
        ]
        
        # Coerce time percentages to numeric while preserving raw blank indicators
        df_melted["TimePercentage"] = pd.to_numeric(df_melted["TimePercentage"], errors="coerce")
        df_melted["IsNoData"] = df_melted["EquipmentName"].isin(blank_eq_names).astype(int)

        all_sheets_data.append(df_melted)

    if not all_sheets_data:
        return pd.DataFrame()

    df_combined = pd.concat(all_sheets_data, ignore_index=True)
    
    # Replace NaN with None for robust SQL compatibility
    return df_combined.where(pd.notnull(df_combined), None)