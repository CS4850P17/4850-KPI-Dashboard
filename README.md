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
