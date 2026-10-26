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

-- Table 2: SAP Goods Movement & Material Consumption Data (Expanded with all raw columns)
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