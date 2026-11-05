
# P17 — Data Understanding

This document records the available datasets, their structures,
potential identifiers, relationships, and KPI data requirements
for the Production Intelligence Dashboard project.

**Project:** CS 4850 - Production Intelligence Dashboard  
**Document Status:** Working Draft V2  
**Reference:** KSU Capstone Sponsor Reference Package v4

**Note:** Confirmed sponsor definitions are distinguished from
preliminary observations and items requiring verification.

---

## 1. Data Sources

The project uses SAP and MES exports provided by the sponsor.
The KPI 2026 workbook is included as a potential reference.

| Source | Dataset | Purpose |
|---|---|---|
| SAP | Production Volume | Production output and quality-related data |
| SAP | Material Consumption | Material movement and consumption analysis |
| MES | Equipment Operation Rate | Equipment operating status and utilization |
| KPI Reference | KPI 2026 | Monthly KPI reference values; exact role to verify |

### Sponsor Reference

According to the Sponsor Reference Package v4:

- Production Volume: Available from SAP production data.
- Yield: Available from SAP grade classification.
- Equipment Utilization: Available from MES equipment-status data.
- Material Consumption: Available as a supporting metric.
- Cell Loss: Source and calculation structure are under review.

The initial project is a read-only analytical proof of concept.
Production-grade SAP/MES integration, write-back, equipment
control, and automated production decisions are outside scope.

---

## 2. Data Structure

### 2.1 SAP Material Consumption

**Source:** SAP

**File:** 3_SAP_Material Consumption Raw Data.XLSX

**Purpose:** Track material movements and support
material consumption analysis.

**Status:** Under review

#### Important Columns

| Column | Description | Expected Type |
|---|---|---|
| Plant | Manufacturing plant identifier | Text |
| Storage location | Storage location identifier | Text |
| Movement type | SAP material movement code | Numeric / code |
| Material | Material identifier | Text |
| Material Description | Material description | Text |
| Batch | Material batch identifier | Text |
| Quantity | Recorded material quantity | Numeric |
| Unit of Entry | Quantity measurement unit | Text |
| Posting Date | Date of material posting | Date |
| Material Document | SAP material document identifier | Text |

#### Findings

- The dataset contains material movement records.
- The observed Movement type value is 311.
- Quantity must be interpreted together with its unit.
- Material movements should not automatically be treated
  as consumption without confirming movement-type rules.
- Row granularity and source-level uniqueness require verification.

#### Row Granularity and Primary Key

**Row Granularity:** Each row appears to represent a
material movement record.

**Candidate Identifiers:**
- Material Document
- Material
- Plant
- Posting Date

**Primary Key Status:** Pending verification

The current SQL schema uses a surrogate primary key
named MovementID.

This identifies database rows but does not automatically
prevent duplicate source transactions.

#### Duplicate Data Investigation

**Status:** Under investigation

- Potential duplicate records were identified during validation.
- Repeated values are not automatically considered errors.
- Similar records may represent different transactions.
- The team is awaiting sponsor guidance on duplicate handling.
- No source records should be removed solely because
  they were flagged by the current duplicate check.

#### Open Questions

- Which fields uniquely identify a source transaction?
- Which movement types represent material consumption?
- Are additional movement types expected?
- How should repeated transactions be identified?

---

### 2.2 SAP Production Volume

**Source:** SAP

**File:** 2_SAP_Prodution Volume Raw Data+PV.xlsx

**Purpose:** Analyze production quantities, product grades,
and output measurements.

**Status:** Under review

#### Worksheets

| Sheet | Structure | Description |
|---|---|---|
| 1) SAP PV | Hierarchical summary | Aggregated MW and PCS values |
| 2) SAP RD (0801) | Tabular data | Material, grade, stock, and movement-related fields |

#### Important Columns

| Column | Description | Expected Type |
|---|---|---|
| Material type | Material classification | Text |
| Storage location | Storage location identifier | Text |
| Material | Material identifier | Text |
| Material Description | Product description | Text |
| Efficiency(WT) | Wattage-related value | Numeric |
| Qgrade | Product quality grade | Text |
| Last Stock | Stock quantity | Numeric |
| GR | Goods receipt-related quantity | Numeric |
| Type | Product/material type; meaning to verify | Text |
| Material Code | Material code | Text |
| PCS | Piece quantity | Numeric |

#### Findings

- The workbook contains two different data structures.
- SAP PV uses grouped row labels rather than a flat table.
- SAP RD contains material, grade, and quantity-related fields.
- The sponsor identifies SAP production data as the source
  for Production Volume and Yield.
- G01 and G02 are classified as Good.
- C is classified as Defect.
- Stock and goods receipt values should not automatically
  be treated as actual production output.
- The exact production confirmation fields require verification.

#### Open Questions

- Which fields represent actual production output?
- Which worksheet should be used for production calculations?
- How are reporting periods identified?
- What source fields uniquely identify production records?

---

### 2.3 MES Equipment Operation Rate

**Source:** MES (Manufacturing Execution System)

**File:** 1_MES_EQP Operation Rate Raw Data.xlsx

**Purpose:** Analyze equipment operating status and utilization.

**Status:** Under review

#### Worksheets

| Sheet | Description |
|---|---|
| 1) Tabber | Tabber equipment operation data |
| 2) Front End | Front-end equipment operation data |
| 3) Back End | Back-end equipment operation data |

#### Data Structure

The dataset uses a wide-format table.

- First column: Equipment status/category.
- Second column: Average values.
- Remaining columns: Individual equipment.
- Rows: Operating states such as RUN, No WIP,
  Kanban Full, and other status categories.

#### Important Fields

| Field | Description | Expected Type |
|---|---|---|
| Equipment Name | Equipment identifier from column header | Text |
| Status | Equipment operating state | Text |
| Average | Reported average for each status | Numeric |
| Operation Rate | Reported equipment status value | Numeric |

#### Findings

- Equipment names are stored as column headers.
- Operating states are stored as rows.
- The workbook contains three equipment groups.
- Values appear to use a percentage scale.
- No confirmed reporting-period field has been identified.
- Equipment identifiers and production-line mapping
  require verification.

#### Python Ingestion Note

The `average` column should not be treated as an
equipment identifier during unpivoting.

Confirm whether the average should be stored separately,
recalculated, or excluded from equipment-level records.

#### Sponsor Reference

Equipment Utilization represents the share of the
applicable analysis period when equipment is in RUN status.

Prototype formula:

Equipment Utilization =
RUN Time / Applicable Reference Time x 100

The exact denominator must still be confirmed.

Original non-RUN categories should remain available
for detailed analysis.

#### Open Questions

- What reporting period does the MES export represent?
- Are equipment names unique across worksheets?
- How are equipment identifiers mapped to production lines?
- Are the values percentages or another time-based measure?
- What is the approved reference time for utilization?

---

### 2.4 KPI 2026

**File:** KPI 2026.xlsx

**Purpose:** Monthly KPI reference and performance data.

**Status:** Pending confirmation

#### Findings

- Contains monthly KPI values.
- Includes production-related indicators.
- May support KPI verification or target comparisons.
- Its role as a source of targets or actual results
  has not been confirmed.

#### Open Questions

- Does the file contain targets, actual results, or both?
- Which KPIs are relevant to P17?
- Should it be integrated into SQL or used only
  as a reference?

---

## 3. Identifiers and Relationships

### 3.1 Candidate Identifiers

The following fields may help identify records across
the available datasets.

These are preliminary candidates and must be verified
before defining source-level uniqueness rules.

| Dataset | Candidate Identifiers | Status |
|---|---|---|
| SAP Material Consumption | Material Document, Material, Plant, Posting Date | To verify |
| SAP Production Volume | Material, Qgrade, reporting period | To verify |
| MES Equipment Operation Rate | Equipment Name, Status, equipment group | To verify |
| KPI 2026 | Fab., Site, Product Name, KPI, Month | To verify |

#### Findings

- No confirmed source-level unique identifiers have been established.
- Some datasets may require composite identifiers.
- Reporting periods may be needed to distinguish records.
- SQL surrogate keys do not establish source transaction uniqueness.
- Duplicate detection rules require further investigation.

---

### 3.2 Potential Relationships

This section identifies possible connections between
SAP, MES, and KPI datasets.

Relationships must be verified before implementation.

| Dataset 1 | Dataset 2 | Potential Connection | Status |
|---|---|---|---|
| SAP Production Volume | SAP Material Consumption | Material, Plant, reporting period | To verify |
| SAP Production Volume | MES Equipment Operation Rate | Production line, reporting period | To verify |
| SAP Production Volume | KPI 2026 | Product, site, reporting month | To verify |
| SAP Material Consumption | KPI 2026 | Material/product mapping, reporting month | To verify |

#### Findings

- SAP datasets may share material-related identifiers.
- SAP and MES do not currently have a confirmed common join key.
- Production line identifiers may require mapping.
- KPI 2026 may be a reference rather than a directly related SQL table.
- The sponsor reference explicitly identifies join keys
  and source-to-target mappings as items requiring confirmation.

---

### 3.3 Production Line Identification

**Status:** Pending confirmation

#### Findings

- Production Line is a recommended dashboard analysis dimension.
- The sponsor reference uses R1, R2, and R3 as example line labels.
- These example labels are not confirmed source-system identifiers.
- SAP Production Volume does not contain an explicit
  Production Line column in the inspected worksheet headers.
- Reviewed columns A, B, C, F, AM, AN, AO, and AP.
- The Type field includes values such as G11,
  which may represent product types.
- Storage location codes are available, but no confirmed
  relationship to production lines has been established.
- MES contains equipment identifiers and equipment groups,
  but no verified equipment-to-line mapping.

#### Open Questions

- How does Qcells identify production lines in SAP and MES?
- Is an equipment-to-production-line mapping available?
- Can storage location codes be mapped to production lines?
- Is line-level analysis required for the initial MVP
  if the provided data does not support it?

---

### 3.4 Date and Time Periods

**Status:** Partially identified

| Dataset | Date/Time Information | Status |
|---|---|---|
| SAP Material Consumption | Posting Date | Identified |
| SAP Production Volume | No confirmed date field in inspected tables | Pending |
| MES Equipment Operation Rate | No confirmed date field in inspected tables | Pending |
| KPI 2026 | Monthly columns (Jan-Dec) | Identified |

#### Findings

- SAP Material Consumption contains Posting Date.
- KPI 2026 organizes values by reporting month.
- The reporting periods represented by SAP Production
  Volume and MES exports have not been confirmed.
- File creation dates should not automatically
  be treated as production dates.
- The sponsor reference recommends date and period
  analysis but does not specify the exact reporting
  periods of the provided exports.

#### Open Questions

- What reporting period does each SAP/MES export cover?
- Does SAP Production Volume contain reporting dates
  outside the inspected table?
- What period do the MES operation percentages represent?
- How should reporting periods be aligned across datasets?

---

## 4. KPI Data Requirements

This section identifies the data sources and fields
needed to calculate the proposed production KPIs.

The Sponsor Reference Package v4 defines four initial
core KPIs and one supporting metric.

### 4.1 KPI Source Mapping

| KPI | Expected Source | Required Data | Status |
|---|---|---|---|
| Production Volume | SAP | Production confirmation quantity, date, line, model, wattage, grade | Field mapping pending |
| Yield | SAP | Good quantity, total produced quantity, grade | Final denominator pending |
| Equipment Utilization | MES | Equipment, RUN status, applicable reference time | Final denominator pending |
| Cell Loss | TBD | Source and calculation fields not yet provided | Sponsor under review |
| Material Consumption (Supporting) | SAP | Material, quantity, movement type, date, batch | Business rules pending |

### 4.2 KPI Calculation Requirements

#### Production Volume

**Sponsor Definition:**
Actual module production for the selected period.

- Aggregate production confirmation records.
- Support PCS and MW analysis where appropriate.
- Analyze by date, line, model, wattage, and grade
  where the source data supports those dimensions.
- Confirm the exact production quantity fields.

#### Yield

**Sponsor Definition:**
Share of produced modules classified as good product.

**Grade Classification:**
- G01 = Good
- G02 = Good
- C = Defect

**Prototype Formula:**

Yield = Good Qty / Total Produced Qty x 100

**Status:** Final denominator requires confirmation.

#### Equipment Utilization

**Sponsor Definition:**
Share of the applicable analysis period during
which equipment is in RUN status.

**Prototype Formula:**

Equipment Utilization =
RUN Time / Applicable Reference Time x 100

- Preserve original non-RUN status categories.
- Confirm the applicable reference time.
- Confirm reporting periods and equipment grouping.

#### Cell Loss

**Sponsor Definition:**
Cell loss during module manufacturing.

**Status:** Under sponsor review.

- The source dataset has not been finalized.
- Detailed calculation rules have not been provided.
- Keep Cell Loss as a placeholder until approved
  data and definitions become available.

#### Material Consumption (Supporting Metric)

**Sponsor Definition:**
Material movement and consumption information
used to support production performance analysis.

- Identify relevant movement types.
- Verify quantity units and conversions.
- Support analysis by material, date, and batch.
- Compare production with consumption only where
  units and business rules support the comparison.

### 4.3 Target vs. Actual

The dashboard is expected to compare actual
production performance against approved targets.

**Current Status:** Pending confirmation

#### Findings

- Target/Plan represents expected performance.
- Actual represents recorded production performance.
- The KPI 2026 workbook contains monthly values,
  but their role as targets or actual results
  has not been confirmed.
- The sponsor reference does not identify a specific
  target-value field in the supplied Excel exports.

#### Open Questions

- Where are approved target values stored?
- Does KPI 2026 contain targets, actual results, or both?
- Are targets defined by line, model, or reporting period?
- What achievement-rate formula should be used?
- How should missing target values be handled?

---

## 5. Open Questions

This section summarizes unresolved questions and
items requiring additional verification.

### 5.1 Data Structure and Identifiers

- Which fields uniquely identify source transactions?
- How are production lines identified across SAP and MES?
- Is an equipment-to-line mapping available?
- What reporting periods do the supplied exports cover?
- Which source fields can be used as reliable join keys?

### 5.2 KPI Definitions

- Which SAP fields represent actual production output?
- What is the approved Yield denominator?
- What reference time should be used for Equipment Utilization?
- Which movement types represent Material Consumption?
- When will the Cell Loss dataset and definition be available?

### 5.3 Target vs. Actual

- Where are approved target values stored?
- Does KPI 2026 contain actual values, targets, or both?
- How are targets defined across lines, models, and periods?
- How should missing targets be handled?

### 5.4 Data Processing and Integration

- How frequently will new SAP and MES files be provided?
- Should the pipeline append new records or update existing ones?
- How should repeated or invalid records be handled?
- Which source fields must be preserved in SQL?
- How should changes in Excel column names be managed?

### 5.5 Pending Confirmations

| Topic | Status | Notes |
|---|---|---|
| Source identifiers | Pending | Verify unique source records |
| Production line mapping | Pending | No confirmed mapping |
| Reporting periods | Pending | SAP Production Volume and MES |
| Production quantity fields | Pending | Confirm source fields |
| Yield denominator | Pending | Prototype formula available |
| Equipment utilization denominator | Pending | Prototype formula available |
| Target values | Pending | Confirm source and meaning |
| Cell Loss | Sponsor Under Review | Additional data and definition expected |
| Duplicate handling | Awaiting Sponsor Response | Team has requested clarification |
| SAP/MES join keys | Pending | Confirm relationships and mappings |

---

## 6. References and Documentation Status

### 6.1 Reference Materials

- KSU Capstone Sponsor Reference Package v4
- SAP Production Volume Raw Data
- SAP Material Consumption Raw Data
- MES Equipment Operation Rate Raw Data
- KPI 2026.xlsx
- sql/schema.sql

### 6.2 Documentation Status

**Completed for V2:**
- Initial data source inventory.
- Preliminary dataset structure documentation.
- Candidate identifier documentation.
- Potential relationship mapping.
- Initial date/time and production line investigation.
- Sponsor-defined KPI business definitions.
- Known limitations and open questions.

**Pending Verification:**
- Source-level unique identifiers.
- Production line mappings.
- Reporting periods.
- Exact KPI source fields.
- Approved target values.
- Final KPI denominators.
- Duplicate handling rules.

**Document Status:** In process

This document should be updated as source fields,
business rules, and sponsor clarifications are verified.
