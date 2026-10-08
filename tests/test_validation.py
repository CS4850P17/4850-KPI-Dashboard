
import pandas as pd

from src.validation import validate_sap, validate_mes


# ==================================================
# 1. SYNTHETIC SAP TEST DATA
# ==================================================
# Contains intentionally invalid data to test:
# - Invalid numeric values
# - Invalid dates
# - Missing values
# - Duplicate records

sap_data = pd.DataFrame({
    "Plant": ["P01", "P01", "P01", "P01"],
    "Storage location": ["S01"] * 4,
    "Movement type": [101] * 4,
    "Material": ["M001", "M002", "M003", "M003"],
    "Material Description": ["Cell A", "Cell B", "Cell C", "Cell C"],
    "Batch": ["B01", "B02", "B03", "B03"],
    "Quantity": [100, "abc", None, None],
    "Unit of Entry": ["EA"] * 4,
    "Posting Date": [
        "2026-10-01",
        "invalid-date",
        "2026-10-03",
        "2026-10-03"
    ],
    "Material Document": ["DOC001", "DOC002", "DOC003", "DOC003"]
})


# ==================================================
# 2. SYNTHETIC MES TEST DATA
# ==================================================
# Contains intentionally invalid equipment values
# and duplicate records.

mes_data = pd.DataFrame({
    "Category": ["RUN", "IDLE", "RUN", "RUN"],
    "EQ01": [80, 20, "abc", "abc"],
    "EQ02": [75, 25, 90, 90]
})


# ==================================================
# 3. RUN SAP VALIDATION
# ==================================================

print("\nTesting SAP validation...")

sap_result = validate_sap(sap_data)
sap_result.print_report()


# ==================================================
# 4. RUN MES VALIDATION
# ==================================================

print("\nTesting MES validation...")

mes_result = validate_mes(mes_data)
mes_result.print_report()


# ==================================================
# 5. VERIFY EXPECTED RESULTS
# ==================================================
# Assertions make the test fail if validation does
# not detect the expected errors and warnings.

assert not sap_result.is_valid()
assert len(sap_result.errors) == 3
assert len(sap_result.warnings) == 1

assert not mes_result.is_valid()
assert len(mes_result.errors) == 1
assert len(mes_result.warnings) == 1

print("\nAll validation tests passed!")
