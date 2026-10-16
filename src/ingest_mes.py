import pandas as pd

def process_mes_file(file_path):
    """Reads a wide-format MES matrix sheet and unpivots equipment columns into rows."""
    df = pd.read_excel(file_path)
    category_col = df.columns[0]
    
    df_melted = pd.melt(
        df, 
        id_vars=[category_col], 
        var_name="EquipmentName", 
        value_name="TimePercentage"
    )
    df_melted.rename(columns={category_col: "Category"}, inplace=True)
    df_melted.dropna(subset=["TimePercentage"], inplace=True)
    df_melted["TimePercentage"] = pd.to_numeric(df_melted["TimePercentage"], errors="coerce")
    df_melted["EquipmentName"] = df_melted["EquipmentName"].str.strip()
    return df_melted