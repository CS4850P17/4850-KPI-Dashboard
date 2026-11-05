CREATE DATABASE ManufacturingKPI;
GO

USE ManufacturingKPI;
GO

-- 1. MES Equipment State Table
CREATE TABLE dbo.Fact_EquipmentState (
    StateID BIGINT IDENTITY(1,1) PRIMARY KEY,
    SheetName VARCHAR(50) NULL,
    Category VARCHAR(100) NOT NULL,
    EquipmentName VARCHAR(100) NOT NULL,
    TimePercentage DECIMAL(8,4) NULL,
    IsNoData INT DEFAULT 0,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- 2. SAP Production Volume Table (Primary RD Source, Excludes ZBOM from Calculations)
CREATE TABLE dbo.Fact_SAP_ProductionVolume (
    VolumeID BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaterialCode VARCHAR(100) NULL,
    MaterialDescription VARCHAR(255) NULL,
    Efficiency_WT DECIMAL(8,2) NULL,
    Qgrade VARCHAR(20) NULL,
    GradeCategory VARCHAR(50) NULL,
    GR_Qty DECIMAL(12,4) NULL,
    ProductionVolume_MW DECIMAL(12,2) NULL,
    IsZBOM INT DEFAULT 0,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- 3. Normalized KPI 2026 Reference Table
CREATE TABLE dbo.Fact_KPI_Reference (
    KPI_ID BIGINT IDENTITY(1,1) PRIMARY KEY,
    [Year] INT NULL,
    [Month] INT NULL,
    Fab VARCHAR(50) NULL,
    Site VARCHAR(50) NULL,
    ProductName VARCHAR(100) NULL,
    KPI VARCHAR(100) NULL,
    Unit VARCHAR(20) NULL,
    [Value] DECIMAL(12,2) NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- 4. SAP Material Movement Table
CREATE TABLE dbo.Fact_SAP_MaterialMovement (
    MovementID BIGINT IDENTITY(1,1) PRIMARY KEY,
    Plant VARCHAR(20) NULL,
    StorageLocation VARCHAR(20) NULL,
    MovementType INT NULL,
    MovementTypeText VARCHAR(255) NULL,
    MaterialCode VARCHAR(50) NULL,
    MaterialDescription VARCHAR(255) NULL,
    Batch VARCHAR(50) NULL,
    Quantity DECIMAL(12,4) NULL,
    UnitOfEntry VARCHAR(20) NULL,
    PostingDate DATE NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- SQL View: Sponsor Yield & Production Volume Calculation View (Excludes ZBOM)
CREATE VIEW dbo.vw_Sponsor_Production_KPIs AS
SELECT 
    MaterialCode,
    MaterialDescription,
    SUM(ProductionVolume_MW) AS Total_Production_MW,
    SUM(CASE WHEN GradeCategory = 'Good' THEN GR_Qty ELSE 0 END) AS Good_Qty,
    SUM(CASE WHEN GradeCategory = 'Defect' THEN GR_Qty ELSE 0 END) AS Defect_Qty,
    ROUND(
        (SUM(CASE WHEN GradeCategory = 'Good' THEN GR_Qty ELSE 0 END) * 100.0) /
        NULLIF(SUM(CASE WHEN GradeCategory IN ('Good', 'Defect') THEN GR_Qty ELSE 0 END), 0), 
        2
    ) AS Yield_Percentage
FROM dbo.Fact_SAP_ProductionVolume
WHERE IsZBOM = 0
GROUP BY MaterialCode, MaterialDescription;
GO