import pandas as pd

class ValidationResult:
    def __init__(self, source):
        self.source = source
        self.errors = []
        self.warnings = []

    def add_error(self, message):
        self.errors.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    def is_valid(self):
        return len(self.errors) == 0

    def print_report(self):
        status = "PASS" if self.is_valid() else "FAIL"
        print(f"\n===== {self.source} VALIDATION ({status}) =====")
        for error in self.errors:
            print(f"[ERROR] {error}")
        for warning in self.warnings:
            print(f"[WARNING] {warning}")

def validate_mes(df):
    result = ValidationResult("MES")
    if df.empty:
        result.add_error("MES dataset is empty.")
    return result

def validate_sap(df):
    result = ValidationResult("SAP")
    if df.empty:
        result.add_error("SAP dataset is empty.")
    return result