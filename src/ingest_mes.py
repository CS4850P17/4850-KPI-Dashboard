import pandas as pd

def process_mes_file(file_path):
    """
    Reads a wide-format MES matrix sheet, unpivots equipment columns into rows,
    and returns a clean DataFrame ready for SQL loading.
    """
    # Read matrix file
    df = pd.read_excel(file_path)
    
    # Identify category column (first column: RUN, No WIP, etc.)
    category_col = df.columns[0]
    
    # Unpivot wide equipment columns into long format
    df_melted = pd.melt(
        df, 
        id_vars=[category_col], 
        var_name="EquipmentName", 
        value_name="TimePercentage"
    )
    
    # Standardize column headers
    df_melted.rename(columns={category_col: "Category"}, inplace=True)
    
    # Clean data types & drop null values
    df_melted.dropna(subset=["TimePercentage"], inplace=True)
    df_melted["TimePercentage"] = pd.to_numeric(df_melted["TimePercentage"], errors="coerce")
    df_melted["EquipmentName"] = df_melted["EquipmentName"].str.strip()
    
    return df_melted
