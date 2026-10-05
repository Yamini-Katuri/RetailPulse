-- ============================================================================
-- RetailPulse — E-Commerce Sales & Customer Analytics
-- Script: sql/data_quality.sql
-- Database Engine: MySQL 8.0+ / ANSI SQL Compatible
-- Purpose: Schema Definition, Table Creation, and Comprehensive Data Quality Audit
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. DATABASE & TABLE DDL DEFINITIONS
-- ----------------------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS retailpulse_db;
USE retailpulse_db;

DROP TABLE IF EXISTS retailpulse_orders;

CREATE TABLE retailpulse_orders (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    region VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    sales DECIMAL(10, 4) NOT NULL,
    quantity INT NOT NULL,
    discount DECIMAL(4, 2) NOT NULL,
    profit DECIMAL(10, 4) NOT NULL,
    order_year INT,
    order_month INT,
    order_year_month VARCHAR(7),
    order_quarter VARCHAR(10),
    order_day_of_week VARCHAR(15),
    shipping_days INT,
    unit_price DECIMAL(10, 4),
    cost DECIMAL(10, 4),
    profit_margin_pct DECIMAL(6, 2),
    discount_tier VARCHAR(50),
    customer_segment VARCHAR(50),
    INDEX idx_order_id (order_id),
    INDEX idx_order_date (order_date),
    INDEX idx_customer_id (customer_id),
    INDEX idx_category (category),
    INDEX idx_region (region)
);

-- ----------------------------------------------------------------------------
-- 2. DATA QUALITY AUDIT QUERIES
-- ----------------------------------------------------------------------------

-- Q2.1: Total Row Count Verification
-- Expected: Exactly 9,994 records
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT row_id) AS unique_row_ids,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS unique_products
FROM retailpulse_orders;

-- Q2.2: Missing / Null Value Audit Across Core Business Columns
-- Expected: 0 nulls across all critical operational fields
SELECT 
    SUM(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 ELSE 0 END) AS missing_order_id,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS missing_order_date,
    SUM(CASE WHEN ship_date IS NULL THEN 1 ELSE 0 END) AS missing_ship_date,
    SUM(CASE WHEN customer_id IS NULL OR TRIM(customer_id) = '' THEN 1 ELSE 0 END) AS missing_customer_id,
    SUM(CASE WHEN product_id IS NULL OR TRIM(product_id) = '' THEN 1 ELSE 0 END) AS missing_product_id,
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS missing_sales,
    SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS missing_quantity,
    SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END) AS missing_profit
FROM retailpulse_orders;

-- Q2.3: Duplicate Order Line Verification
-- Identifies if the same product was recorded multiple times under the same order ID
SELECT 
    order_id, 
    product_id, 
    COUNT(*) AS duplicate_line_count
FROM retailpulse_orders
GROUP BY order_id, product_id
HAVING COUNT(*) > 1;

-- Q2.4: Date Chronology & Logical Integrity Check
-- Ensures ship_date is never earlier than order_date
SELECT 
    COUNT(*) AS invalid_shipping_date_count,
    MIN(DATEDIFF(ship_date, order_date)) AS min_shipping_days,
    MAX(DATEDIFF(ship_date, order_date)) AS max_shipping_days,
    ROUND(AVG(DATEDIFF(ship_date, order_date)), 2) AS avg_shipping_days
FROM retailpulse_orders;

-- Q2.5: Numerical Boundary & Anomaly Validation
-- Validates range bounds: sales > 0, quantity >= 1, discount between 0 and 1
SELECT 
    MIN(sales) AS min_sales,
    MAX(sales) AS max_sales,
    MIN(quantity) AS min_quantity,
    MAX(quantity) AS max_quantity,
    MIN(discount) AS min_discount,
    MAX(discount) AS max_discount,
    MIN(profit) AS min_profit,
    MAX(profit) AS max_profit,
    SUM(CASE WHEN sales <= 0 THEN 1 ELSE 0 END) AS non_positive_sales_count,
    SUM(CASE WHEN quantity < 1 THEN 1 ELSE 0 END) AS invalid_quantity_count,
    SUM(CASE WHEN discount < 0 OR discount > 1 THEN 1 ELSE 0 END) AS invalid_discount_count
FROM retailpulse_orders;
