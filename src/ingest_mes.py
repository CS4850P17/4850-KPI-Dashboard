import pandas as pd

def process_mes_file(file_path):
    """Reads all sheets (Tabber, Front End, Back End) from the MES file and melts them."""
    xls = pd.ExcelFile(file_path)
    all_sheets_data = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        if df.empty:
            continue
        
        category_col = df.columns[0]
        
        df_melted = pd.melt(
            df, 
            id_vars=[category_col], 
            var_name="EquipmentName", 
            value_name="TimePercentage"
        )
        df_melted.rename(columns={category_col: "Category"}, inplace=True)
        df_melted["SheetName"] = sheet_name.strip()
        
        # Clean types & drop nulls
        df_melted.dropna(subset=["TimePercentage"], inplace=True)
        df_melted["TimePercentage"] = pd.to_numeric(df_melted["TimePercentage"], errors="coerce")
        df_melted["EquipmentName"] = df_melted["EquipmentName"].astype(str).str.strip()
        
        # Filter out summary / average columns
        exclude_keywords = ["average", "total", "sum", "mean"]
        df_melted = df_melted[
            ~df_melted["EquipmentName"].str.lower().isin(exclude_keywords)
        ]
        
        all_sheets_data.append(df_melted)

    if not all_sheets_data:
        return pd.DataFrame()

    return pd.concat(all_sheets_data, ignore_index=True)