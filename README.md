# 4850-KPI-Dashboard
CS 4850 Senior project Power BI Dashboard

This is a capstone project using end-to-end data analytics solution built using real industry manufacturing data provided by a project sponsor.

The goal of the project is to take raw Excel files, clean and validate the data with Python, store the processed data in Microsoft SQL Server, calculate key manufacturing performance metrics, and present the results in an interactive Power BI dashboard.

## Technologies

- Python
- Pandas
- Microsoft SQL Server
- SQL
- Microsoft Power BI
- Microsoft Excel
- Git / GitHub

## Project Workflow

```text
Excel Files
     ↓
Python
Data Cleaning & Validation
     ↓
SQL Server
Data Storage & Processing
     ↓
Power BI
Dashboard & Analysis
```

## Key Features

The project includes:

- Automated Excel data ingestion
- Data cleaning and transformation
- Missing-value and duplicate detection
- Data type and identifier validation
- SQL Server database integration
- Manufacturing KPI calculations
- Interactive Power BI dashboards
- Data quality monitoring
- Testing and validation

## KPIs

The dashboard will analyze metrics such as:

- Production Volume
- Yield
- Equipment Utilization
- Achievement Rate
- Performance Gap
- Material Consumption
- Cell Loss, if available

## Power BI Dashboard

The dashboard will include four main areas:

- **Overview** – high-level production KPIs
- **Production Analysis** – production trends and comparisons
- **Investigation** – drill-down analysis by line, equipment, model, and time
- **Data Quality** – missing data, duplicates, invalid records, and pipeline issues

## Repository Structure

```text
project/
│
├── data/
├── src/
├── sql/
├── powerbi/
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

## Data Privacy

The project uses industry-sponsored data. Confidential or proprietary sponsor data is not included in this public repository. Only approved, anonymized, or sample data will be used for demonstration purposes.

## Status

🚧 **Currently in development**

The project is being developed as part of a university capstone project and will be updated as the Python pipeline, SQL database, KPI calculations, and Power BI dashboard are completed.

## Integrated pipeline usage

The entry point is `main.py`. Place approved Excel workbooks in `data/raw/`.

```bash
pip install -r requirements.txt
python main.py
```

This runs the new **`preprocessing(excel_file)` function in `main.py`** for the three-sheet MES equipment workbook and uses the existing `src/ingest_sap.py`, `src/ingest_mes.py`, and `src/validation.py` for other supported workbooks. Four MES CSV reports and `analysis.json` appear under `data/processed/`.

To append to the team's pre-existing SQL Server fact tables, configure the `DB_*` environment variables shown in `.env.example`, confirm the database schema, then run:

```bash
python main.py --load-sql
```

**Important:** SQL mode appends and can create duplicate records when rerun. It is off by default. Database access was not tested. MES RUN percentage is provisional; all-zero records are flagged instead of silently treated as valid. Do not commit actual sponsor workbooks, processed sponsor data, or credentials.

The original uploaded `import_to_sql.py` is *not* included in this package because it contains a hard-coded SQL password and overlapping ingestion logic. That credential should be rotated if it is active. The previous `config.py` also contained a typo (`os.gatenv`) fixed in `src/config.py`.
