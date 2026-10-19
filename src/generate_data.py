import pandas as pd
import numpy as np

# 1. Define data range & lines
dates = pd.date_range(start="2026-09-28", end="2026-10-04")
lines = ["Line A / M-100", "Line B / M-200", "Line C / M-300"]

data = []
np.random.seed(42)

for date in dates:
    for line in lines:
        base_pcs = np.random.randint(13500, 15500)
        mw_val = round(np.random.uniform(0.015, 0.022), 5)

        if "Line B" in line and date.strftime("%Y-%m-%d") in ["2026-10-01", "2026-10-02"]:
            base_pcs = np.random.randint(9500,11000)

        data.append({
            "Posting Date": date.strftime("%Y-%m-%d"),
            "Row Labels": line,
            "PCS": base_pcs,
            "MW": mw_val
        })

df_pv = pd.DataFrame(data)

df_pv.to_csv("synthetic_SAP_PV.csv", index=False)
print("Synthetic SAP PV data generated successfully!")

