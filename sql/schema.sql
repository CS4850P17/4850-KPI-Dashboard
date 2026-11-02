CREATE DATABASE ManufacturingKPI;
GO

USE ManufacturingKPI;
GO

-- Table 1: MES Equipment State & OEE Data (Multi-Sheet: Tabber, Front End, Back End)
CREATE TABLE dbo.Fact_EquipmentState (
    StateID BIGINT IDENTITY(1,1) PRIMARY KEY,
    SheetName VARCHAR(50) NULL,
    LogDate DATE NULL,
    EquipmentName VARCHAR(100) NOT NULL,
    Category VARCHAR(100) NOT NULL,
    TimePercentage DECIMAL(8,4) NOT NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- Table 2: SAP Production Volume (Sheet: 1) SAP PV)
CREATE TABLE dbo.Fact_SAP_ProductionVolume (
    VolumeID BIGINT IDENTITY(1,1) PRIMARY KEY,
    RowLabels VARCHAR(100) NULL,
    MW DECIMAL(12,4) NULL,
    PCS DECIMAL(12,4) NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- Table 3: SAP Raw Data & Stock Status (Sheet: 2) SAP RD (0801))
CREATE TABLE dbo.Fact_SAP_RawData (
    RawDataID BIGINT IDENTITY(1,1) PRIMARY KEY,
    Materialtype VARCHAR(50) NULL,
    Storagelocation VARCHAR(20) NULL,
    Material VARCHAR(50) NULL,
    MaterialDescription VARCHAR(255) NULL,
    Efficiency_WT_ DECIMAL(8,2) NULL,
    Qgrade VARCHAR(20) NULL,
    LastStock DECIMAL(12,4) NULL,
    WTLastStock DECIMAL(12,4) NULL,
    GR DECIMAL(12,4) NULL,
    WTGR DECIMAL(12,4) NULL,
    Sum_Total DECIMAL(12,4) NULL,
    PCS DECIMAL(12,4) NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO

-- Table 4: SAP Material Movement & Consumption Data
CREATE TABLE dbo.Fact_SAP_MaterialMovement (
    MovementID BIGINT IDENTITY(1,1) PRIMARY KEY,
    Plant VARCHAR(20) NULL,
    StorageLocation VARCHAR(20) NULL,
    MovementType INT NULL,
    MovementTypeText VARCHAR(255) NULL,
    BillOfLading VARCHAR(50) NULL,
    ReceivingPlant VARCHAR(20) NULL,
    ReceivingStorageLocation VARCHAR(20) NULL,
    MaterialCode VARCHAR(50) NULL,
    GoodsRecipient VARCHAR(100) NULL,
    MaterialDescription VARCHAR(255) NULL,
    DocumentHeaderText VARCHAR(255) NULL,
    Batch VARCHAR(50) NULL,
    PurchaseOrder VARCHAR(50) NULL,
    Quantity DECIMAL(12,4) NULL,
    UnitOfEntry VARCHAR(20) NULL,
    MaterialDocument VARCHAR(50) NULL,
    PostingDate DATE NULL,
    DocumentDate DATE NULL,
    EntryDate DATE NULL,
    TimeOfEntry TIME NULL,
    UserName VARCHAR(50) NULL,
    Text VARCHAR(255) NULL,
    Supplier VARCHAR(100) NULL,
    AmountLocalCurrency DECIMAL(15,2) NULL,
    Currency VARCHAR(10) NULL,
    [Order] VARCHAR(50) NULL,
    Reservation VARCHAR(50) NULL,
    Reference VARCHAR(50) NULL,
    Item INT NULL,
    EnteredOnEST DATE NULL,
    TimeOfEntryEST TIME NULL,
    DebitCreditIndicator VARCHAR(5) NULL,
    CostCenter VARCHAR(50) NULL,
    SourceFileName VARCHAR(255) NULL,
    IngestedAt DATETIME DEFAULT GETDATE()
);
GO