-- ============================================================================
-- CS 4850 Senior Project: SQL Server Database Setup
-- Manufacturing KPI Dashboard Pipeline
-- ============================================================================

-- 1. Create Database 
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'ManufacturingKPI')
BEGIN
  CREATE DATABASE ManufacturingKPI;
END
GO

USE ManufacturingKPI;
GO

-- ============================================================================
-- 2. FACT & STAGING TABLES FOR MES & SAP INGESTION
-- ============================================================================

-- Table 1: MES Equipment State & OEE Data (Unpivoted Matrix Format)
IF OBJECT_ID('dbo.Fact_EquipmentState', 'U') IS NOT NULL 
  DROP TABLE dbo.Fact_EquipmentState;
GO

CREATE TABLE dbo.Fact_EquipmentState (
  StateID BIGINT IDENTITY(1,1) PRIMARY KEY,
  LogDate DATE NULL,                             -- Inferred or extracted date
  EquipmentName VARCHAR(100) NOT NULL,          -- e.g., 'tabber #1', 'front eva layup'
  Category VARCHAR(100) NOT NULL,               -- e.g., 'RUN', 'No WIP', 'Tool Cleaning', 'Down by Machine'
  TimePercentage DECIMAL(8,4) NOT NULL,         -- Value from spreadsheet cell (e.g. 72.50)
  SourceFileName VARCHAR(255) NULL,
  IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- Table 2: SAP Goods Movement & Material Consumption Data
IF OBJECT_ID('dbo.Fact_SAP_MaterialMovement', 'U') IS NOT NULL 
  DROP TABLE dbo.Fact_SAP_MaterialMovement;
GO

CREATE TABLE dbo.Fact_SAP_MaterialMovement (
  MovementID BIGINT IDENTITY(1,1) PRIMARY KEY,
  Plant VARCHAR(20) NOT NULL,                    -- e.g., 'P313'
  StorageLocation VARCHAR(20) NOT NULL,          -- e.g., 'PRT3'
  MovementType INT NOT NULL,                     -- e.g., 311 (Transfer within plant)
  MaterialCode VARCHAR(50) NOT NULL,             -- e.g., 'CF02G02-0192'
  MaterialDescription VARCHAR(255) NULL,         -- e.g., 'Q8HQUP16-G2.01...'
  Batch VARCHAR(50) NULL,
  Quantity DECIMAL(12,4) NOT NULL,
  UnitOfEntry VARCHAR(10) NOT NULL,              -- e.g., 'PCS', 'EA'
  PostingDate DATE NOT NULL,
  EntryTime TIME NULL,
  MaterialDocument VARCHAR(50) NOT NULL,
  SourceFileName VARCHAR(255) NULL,
  IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- Table 3: Pipeline Audit & Data Quality Logs (For Power BI Quality Page)
IF OBJECT_ID('dbo.Log_DataQualityIssues', 'U') IS NOT NULL 
  DROP TABLE dbo.Log_DataQualityIssues;
GO

CREATE TABLE dbo.Log_DataQualityIssues (
  IssueID BIGINT IDENTITY(1,1) PRIMARY KEY,
  SourceFileName VARCHAR(255) NOT NULL,
  RowNumber INT NULL,
  ColumnName VARCHAR(100) NULL,
  IssueType VARCHAR(50) NOT NULL,                -- 'MISSING_VALUE', 'DUPLICATE', 'TYPE_ERROR'
  ErrorMessage VARCHAR(500) NOT NULL,
  LoggedAt DATETIME DEFAULT GETDATE()
);
GO

-- ----------------------------------------------------------------------------
-- 3. REPORTING VIEWS FOR POWER BI
-- ----------------------------------------------------------------------------

-- View 1: Equipment Utilization & Loss Summary
CREATE OR ALTER VIEW dbo.View_EquipmentUtilizationSummary AS
SELECT 
  EquipmentName,
  Category,
  AVG(TimePercentage) AS AvgTimePercentage,
  COUNT(*) AS RecordCount
FROM dbo.Fact_EquipmentState
GROUP BY EquipmentName, Category;
GO

-- View 2: SAP Material Consumption Summary
CREATE OR ALTER VIEW dbo.View_MaterialConsumptionSummary AS
SELECT 
  Plant,
  StorageLocation,
  MaterialCode,
  MaterialDescription,
  UnitOfEntry,
  PostingDate,
  SUM(Quantity) AS TotalQuantityTransferred
FROM dbo.Fact_SAP_MaterialMovement
GROUP BY Plant, StorageLocation, MaterialCode, MaterialDescription, UnitOfEntry, PostingDate;
GO
