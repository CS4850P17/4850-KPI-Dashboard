CREATE DATABASE ManufacturingKPI;
GO

USE ManufacturingKPI;
GO

-- Table 1: MES Equipment State & OEE Data
CREATE TABLE dbo.Fact_EquipmentState (
    StateID BIGINT IDENTITY(1,1) PRIMARY KEY,
    LogDate DATE NULL,
    EquipmentName VARCHAR(100) NOT NULL,
    Category VARCHAR(100) NOT NULL,
    TimePercentage DECIMAL(8,4) NOT NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- Table 2: SAP Goods Movement & Material Consumption Data
CREATE TABLE dbo.Fact_SAP_MaterialMovement (
    MovementID BIGINT IDENTITY(1,1) PRIMARY KEY,
    Plant VARCHAR(20) NOT NULL,
    StorageLocation VARCHAR(20) NOT NULL,
    MovementType INT NOT NULL,
    MaterialCode VARCHAR(50) NOT NULL,
    MaterialDescription VARCHAR(255) NULL,
    Batch VARCHAR(50) NULL,
    Quantity DECIMAL(12,4) NOT NULL,
    UnitOfEntry VARCHAR(10) NOT NULL,
    PostingDate DATE NOT NULL,
    MaterialDocument VARCHAR(50) NOT NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO