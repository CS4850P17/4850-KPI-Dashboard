
import pandas as pd


# ==================================================
# 1. SAP REQUIRED COLUMNS
# ==================================================
# These column names match the raw SAP Excel headers
# expected by ingest_sap.py.
#
# IMPORTANT:
# Update this list if the SAP export format changes.
# These are currently treated as required by the
# ingestion code, not necessarily by every business rule.

from src.ingest_sap import column_mapping

SAP_REQUIRED_COLUMNS = list(column_mapping.keys())


# ==================================================
# 2. VALIDATION RESULT
# ==================================================
# Stores validation errors and warnings in one place.
#
# Errors:
#   Problems that cause validation to fail.
#
# Warnings:
#   Potential issues that require review but do not
#   automatically cause validation to fail.
#
# This class does not modify the original dataset.

class ValidationResult:

    def __init__(self, source):
        """Initialize an empty report for SAP or MES."""
        self.source = source
        self.errors = []
        self.warnings = []

    def add_error(self, message):
        """Record a validation error."""
        self.errors.append(message)

    def add_warning(self, message):
        """Record a potential data quality issue."""
        self.warnings.append(message)

    def is_valid(self):
        """Return True when no errors were detected."""
        return len(self.errors) == 0

    def print_report(self):
        """Display a readable summary of validation results."""
        status = "PASS" if self.is_valid() else "FAIL"

        print(f"\n===== {self.source} VALIDATION =====")
        print(f"Status: {status}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        for error in self.errors:
            print(f"[ERROR] {error}")

        for warning in self.warnings:
            print(f"[WARNING] {warning}")


# ==================================================
# 3. REQUIRED COLUMN VALIDATION
# ==================================================
# Checks whether all expected columns exist.
#
# This should run before transformation because
# missing SAP columns can cause a KeyError when
# ingest_sap.py selects columns from the DataFrame.

def validate_required_columns(df, required_columns, result):

    """Report missing column names."""
    for column in required_columns:
        if column not in df.columns:
            result.add_error(
                f"Missing required column: {column}"
            )


# ==================================================
# 4. MISSING VALUE VALIDATION
# ==================================================
# Checks selected columns for empty or null values.
#
# Missing values are reported, not automatically
# replaced or deleted. Replacing missing production
# data with zero could change the meaning of the data.

def validate_missing_values(df, columns, result):
    """Report null values in selected columns."""

    for column in columns:

        # Missing columns are handled separately by
        # the required-column validation function.
        if column not in df.columns:
            continue

        missing_count = df[column].isna().sum()

        if missing_count > 0:
            result.add_error(
                f"{column} contains {missing_count} missing values"
            )


# ==================================================
# 5. NUMERIC DATA TYPE VALIDATION
# ==================================================
# Checks whether non-empty values can be converted
# into numeric data.
#
# errors="coerce" converts invalid values to NaN
# in a temporary Series. It does not modify df.
#
# Missing values are excluded here because they
# are handled by the missing-value validation.

def validate_numeric_columns(df, columns, result):
    """Report values that cannot be converted to numbers."""

    for column in columns:

        if column not in df.columns:
            continue

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # A value is invalid if the original value
        # exists but numeric conversion fails.
        invalid_mask = (
            df[column].notna() & converted.isna()
        )

        invalid_count = invalid_mask.sum()

        if invalid_count > 0:
            result.add_error(
                f"{column} contains {invalid_count} invalid numeric values"
            )


# ==================================================
# 6. DATE VALIDATION
# ==================================================
# Checks whether non-empty date values can be parsed.
#
# Invalid dates are reported instead of automatically
# corrected because the intended date may be unclear.
#
# NOTE:
# Date format requirements must be confirmed with
# the sponsor before enforcing a specific format.

def validate_date_columns(df, columns, result):
    """Report date values that cannot be parsed."""

    for column in columns:

        if column not in df.columns:
            continue

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid_mask = (
            df[column].notna() & converted.isna()
        )

        invalid_count = invalid_mask.sum()

        if invalid_count > 0:
            result.add_error(
                f"{column} contains {invalid_count} invalid dates"
            )


# ==================================================
# 7. DUPLICATE RECORD VALIDATION
# ==================================================
# Detects potential duplicate rows.
#
# If key_columns is provided, duplicates are checked
# using only those columns.
#
# Otherwise, the entire row is compared.
#
# Duplicates are warnings for now because repeated
# manufacturing records are not always incorrect.
#
# TODO:
# Confirm the correct unique identifiers with
# the sponsor before treating duplicates as errors.

def validate_duplicates(df, result, key_columns=None):
    """Report potential duplicate records."""

    if key_columns is None:
        duplicates = df.duplicated()

    else:
        # Avoid checking partial keys when a required
        # identifier column is missing.
        if not all(col in df.columns for col in key_columns):
            return

        duplicates = df.duplicated(
            subset=key_columns
        )

    duplicate_count = duplicates.sum()

    if duplicate_count > 0:
        result.add_warning(
            f"Found {duplicate_count} potential duplicate records"
        )


# ==================================================
# 8. SAP VALIDATION
# ==================================================
# Main entry point for validating raw SAP Excel data.
#
# This function combines the individual checks and
# returns a ValidationResult object.
#
# It should be called after reading the raw Excel
# file but before SAP data transformation.
#
# The required columns match ingest_sap.py.
# The selected non-null fields are provisional
# validation rules and need sponsor confirmation.

def validate_sap(df):
    """Run the current validation checks for raw SAP data."""

    result = ValidationResult("SAP")

    validate_required_columns(
        df,
        SAP_REQUIRED_COLUMNS,
        result
    )

    validate_missing_values(
        df,
        ["Plant", "Material", "Quantity", "Posting Date"],
        result
    )

    validate_numeric_columns(
        df,
        ["Quantity", "Movement type"],
        result
    )

    validate_date_columns(
        df,
        ["Posting Date"],
        result
    )

    validate_duplicates(
        df,
        result
    )

    return result


# ==================================================
# 9. MES VALIDATION
# ==================================================
# Main entry point for validating raw MES Excel data.
#
# MES data is expected to use a wide-format matrix:
#   First column  = production status/category
#   Other columns = equipment values
#
# This follows the structure expected by ingest_mes.py.
#
# TODO:
# Confirm equipment identifiers, valid categories,
# percentage units, and allowed numeric ranges.
#
# The current checks do not enforce percentage limits
# or validate the meaning of equipment identifiers.

def validate_mes(df):
    """Run the current validation checks for raw MES data."""

    result = ValidationResult("MES")

    # An empty dataset cannot be processed reliably.
    if df.empty:
        result.add_error("MES dataset is empty")
        return result

    # At least one category column and one equipment
    # column are needed for the MES unpivot operation.
    if len(df.columns) < 2:
        result.add_error(
            "MES dataset must contain a category column and equipment columns"
        )
        return result

    category_column = df.columns[0]
    equipment_columns = df.columns[1:]

    validate_missing_values(
        df,
        [category_column],
        result
    )

    validate_numeric_columns(
        df,
        equipment_columns,
        result
    )

    validate_duplicates(
        df,
        result
    )

    return result
