-- ============================================================================
-- RetailPulse — E-Commerce Sales & Customer Analytics
-- Script: sql/sales_analysis.sql
-- Database Engine: MySQL 8.0+ / ANSI SQL Compatible
-- Purpose: Executive Sales KPIs, Temporal Trends, Seasonality, and Discount Impact
-- ============================================================================

USE retailpulse_db;

-- ----------------------------------------------------------------------------
-- 1. EXECUTIVE OVERALL SALES & REVENUE KPIs
-- ----------------------------------------------------------------------------
-- Business Question: What is the total top-line revenue, net profit, order volume,
-- units sold, overall profit margin, and average order value?

SELECT 
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS overall_profit_margin_pct,
    COUNT(DISTINCT order_id) AS total_distinct_orders,
    COUNT(row_id) AS total_order_line_items,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT customer_id) AS total_unique_customers,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value_aov,
    ROUND(SUM(sales) / SUM(quantity), 2) AS average_revenue_per_unit,
    ROUND(AVG(shipping_days), 2) AS avg_shipping_duration_days
FROM retailpulse_orders;

-- ----------------------------------------------------------------------------
-- 2. ANNUAL SALES GROWTH & YEAR-OVER-YEAR (YoY) ANALYSIS (CTE + LAG)
-- ----------------------------------------------------------------------------
-- Business Question: How has annual revenue and profit evolved from 2014 to 2017,
-- and what is the YoY revenue growth percentage?

WITH annual_summary AS (
    SELECT 
        order_year,
        ROUND(SUM(sales), 2) AS annual_revenue,
        ROUND(SUM(profit), 2) AS annual_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM retailpulse_orders
    GROUP BY order_year
)
SELECT 
    order_year,
    annual_revenue,
    annual_profit,
    profit_margin_pct,
    total_orders,
    active_customers,
    LAG(annual_revenue, 1) OVER (ORDER BY order_year) AS prior_year_revenue,
    ROUND(
        ((annual_revenue - LAG(annual_revenue, 1) OVER (ORDER BY order_year)) / 
        LAG(annual_revenue, 1) OVER (ORDER BY order_year)) * 100, 
        2
    ) AS yoy_sales_growth_pct
FROM annual_summary
ORDER BY order_year;

-- ----------------------------------------------------------------------------
-- 3. MONTHLY REVENUE & PROFIT TRAJECTORY (TIME-SERIES)
-- ----------------------------------------------------------------------------
-- Business Question: What are the monthly sales trends, and are profit margins 
-- remaining healthy throughout the year?

SELECT 
    order_year,
    order_month,
    order_year_month,
    ROUND(SUM(sales), 2) AS monthly_revenue,
    ROUND(SUM(profit), 2) AS monthly_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS monthly_profit_margin_pct,
    COUNT(DISTINCT order_id) AS monthly_orders,
    SUM(quantity) AS monthly_units_sold
FROM retailpulse_orders
GROUP BY order_year, order_month, order_year_month
ORDER BY order_year, order_month;

-- ----------------------------------------------------------------------------
-- 4. QUARTERLY SALES SEASONALITY ANALYSIS
-- ----------------------------------------------------------------------------
-- Business Question: Does the business exhibit recurring quarterly seasonality, 
-- and which quarter generates peak demand?

WITH quarterly_metrics AS (
    SELECT 
        order_quarter,
        ROUND(SUM(sales), 2) AS quarterly_revenue,
        ROUND(SUM(profit), 2) AS quarterly_profit,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(quantity) AS units_sold
    FROM retailpulse_orders
    GROUP BY order_quarter
)
SELECT 
    order_quarter,
    quarterly_revenue,
    quarterly_profit,
    ROUND((quarterly_profit / quarterly_revenue) * 100, 2) AS profit_margin_pct,
    total_orders,
    units_sold,
    ROUND((quarterly_revenue / SUM(quarterly_revenue) OVER ()) * 100, 2) AS revenue_share_pct
FROM quarterly_metrics
ORDER BY order_quarter;

-- ----------------------------------------------------------------------------
-- 5. DAY OF WEEK TRANSACTION & REVENUE PATTERNS
-- ----------------------------------------------------------------------------
-- Business Question: Which days of the week experience the highest purchase volume?

SELECT 
    order_day_of_week,
    COUNT(DISTINCT order_id) AS distinct_orders,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_line_item_value
FROM retailpulse_orders
GROUP BY order_day_of_week
ORDER BY distinct_orders DESC;

-- ----------------------------------------------------------------------------
-- 6. SHIPPING MODE REVENUE CONTRIBUTION & LOGISTICS EFFICIENCY
-- ----------------------------------------------------------------------------
-- Business Question: How do different shipping tiers perform in terms of sales 
-- volume, average shipping duration, and SLA adherence?

SELECT 
    ship_mode,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(row_id) AS line_items,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND((SUM(sales) / (SELECT SUM(sales) FROM retailpulse_orders)) * 100, 2) AS revenue_share_pct,
    ROUND(AVG(shipping_days), 2) AS avg_shipping_days,
    MAX(shipping_days) AS max_shipping_days,
    SUM(CASE WHEN is_shipping_delayed = 1 THEN 1 ELSE 0 END) AS delayed_orders_count,
    ROUND((SUM(CASE WHEN is_shipping_delayed = 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS delayed_order_pct
FROM retailpulse_orders
GROUP BY ship_mode
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- 7. REGIONAL SALES & PROFIT MARGIN DISPARITY
-- ----------------------------------------------------------------------------
-- Business Question: Which geographic regions generate the most sales, and why 
-- do profit margins diverge significantly across territories?

SELECT 
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND((SUM(sales) / (SELECT SUM(sales) FROM retailpulse_orders)) * 100, 2) AS revenue_share_pct,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / (SELECT SUM(profit) FROM retailpulse_orders)) * 100, 2) AS profit_share_pct,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS regional_profit_margin_pct,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_pct
FROM retailpulse_orders
GROUP BY region
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- 8. THE DISCOUNT TRAP: IMPACT OF DISCOUNT TIERS ON PROFITABILITY
-- ----------------------------------------------------------------------------
-- Business Question: At what discount threshold does transaction profitability 
-- collapse into negative margins?

SELECT 
    discount_tier,
    COUNT(row_id) AS transaction_count,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit), 2) AS avg_profit_per_transaction,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_making_transactions,
    ROUND((SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(row_id)) * 100, 2) AS loss_rate_pct
FROM retailpulse_orders
GROUP BY discount_tier
ORDER BY 
    CASE 
        WHEN discount_tier = '0% (No Discount)' THEN 1
        WHEN discount_tier = '1% - 20% (Low)' THEN 2
        WHEN discount_tier = '21% - 40% (Moderate)' THEN 3
        ELSE 4
    END;
