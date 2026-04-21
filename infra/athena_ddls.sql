-- Base de datos
CREATE DATABASE IF NOT EXISTS chinook_dw;

USE chinook_dw;


-- =========================
-- DIM CUSTOMER
-- =========================
CREATE EXTERNAL TABLE IF NOT EXISTS dim_customer (
    CustomerKey INT,
    FirstName STRING,
    LastName STRING,
    Company STRING,
    Country STRING,
    City STRING,
    State STRING,
    Email STRING
)
STORED AS PARQUET
LOCATION 's3://chinook-datalake-academy/dim_customer/';


-- =========================
-- DIM TRACK
-- =========================
CREATE EXTERNAL TABLE IF NOT EXISTS dim_track (
    TrackKey INT,
    Name STRING,
    Album STRING,
    Artist STRING,
    Genre STRING,
    MediaType STRING,
    Composer STRING,
    Milliseconds INT
)
STORED AS PARQUET
LOCATION 's3://chinook-datalake-academy/dim_track/';


-- =========================
-- DIM EMPLOYEE
-- =========================
CREATE EXTERNAL TABLE IF NOT EXISTS dim_employee (
    EmployeeKey INT,
    FirstName STRING,
    LastName STRING,
    Title STRING,
    ReportsTo INT,
    HireDate TIMESTAMP,
    Email STRING
)
STORED AS PARQUET
LOCATION 's3://chinook-datalake-academy/dim_employee/';


-- =========================
-- DIM DATE (TUYA)
-- =========================
CREATE EXTERNAL TABLE IF NOT EXISTS dim_date (
    DateKey INT,
    FullDate DATE,
    Year INT,
    Quarter INT,
    Month INT,
    Day INT,
    DayOfWeek STRING,
    IsHoliday BOOLEAN
)
STORED AS PARQUET
LOCATION 's3://chinook-datalake-academy/dim_date/';


-- =========================
-- FACT SALES (PARTICIONADA)
-- =========================
CREATE EXTERNAL TABLE IF NOT EXISTS fact_sales (
    CustomerKey INT,
    TrackKey INT,
    InvoiceDateKey INT,
    EmployeeKey INT,
    Quantity INT,
    UnitPrice DOUBLE,
    TotalAmount DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT,
    day INT
)
STORED AS PARQUET
LOCATION 's3://chinook-datalake-academy/fact_sales/';


-- =========================
-- CARGAR PARTICIONES
-- =========================
MSCK REPAIR TABLE fact_sales;