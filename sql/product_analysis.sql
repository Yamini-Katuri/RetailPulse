-- ============================================================================
-- RetailPulse — E-Commerce Sales & Customer Analytics
-- Script: sql/product_analysis.sql
-- Database Engine: MySQL 8.0+ / ANSI SQL Compatible
-- Purpose: Category, Sub-Category, and Product-Level Performance Analysis
-- ============================================================================

USE retailpulse_db;

-- ----------------------------------------------------------------------------
-- 1. CATEGORY-LEVEL PERFORMANCE & REVENUE CONTRIBUTION
-- ----------------------------------------------------------------------------
-- Business Question: What is the total revenue, profit, units sold, and profit 
-- margin across the three major product categories?

SELECT 
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND((SUM(sales) / SUM(SUM(sales)) OVER ()) * 100, 2) AS revenue_share_pct,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(SUM(profit)) OVER ()) * 100, 2) AS profit_share_pct,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_pct
FROM retailpulse_orders
GROUP BY category
ORDER BY total_revenue DESC;

-- ----------------------------------------------------------------------------
-- 2. SUB-CATEGORY PROFITABILITY & LOSS RATE RANKING
-- ----------------------------------------------------------------------------
-- Business Question: Which sub-categories are the top profit engines, and which 
-- ones are causing massive financial losses?

SELECT 
    category,
    sub_category,
    COUNT(row_id) AS order_lines,
    SUM(quantity) AS units_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_pct,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_making_orders,
    ROUND((SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(row_id)) * 100, 2) AS loss_order_rate_pct
FROM retailpulse_orders
GROUP BY category, sub_category
ORDER BY total_profit DESC;

-- ----------------------------------------------------------------------------
-- 3. TOP 10 REVENUE-GENERATING PRODUCTS (WINDOW FUNCTION: DENSE_RANK)
-- ----------------------------------------------------------------------------
-- Business Question: What are the top 10 individual products generating the highest 
-- sales volume, and are they profitable?

WITH product_sales AS (
    SELECT 
        product_id,
        product_name,
        category,
        sub_category,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(sales), 2) AS total_revenue,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
        DENSE_RANK() OVER (ORDER BY SUM(sales) DESC) AS revenue_rank
    FROM retailpulse_orders
    GROUP BY product_id, product_name, category, sub_category
)
SELECT 
    revenue_rank,
    product_name,
    category,
    sub_category,
    total_units_sold,
    total_revenue,
    total_profit,
    profit_margin_pct
FROM product_sales
WHERE revenue_rank <= 10
ORDER BY revenue_rank;

-- ----------------------------------------------------------------------------
-- 4. TOP 10 MOST PROFITABLE PRODUCTS
-- ----------------------------------------------------------------------------
-- Business Question: Which specific products contribute the greatest net profit?

WITH product_profit AS (
    SELECT 
        product_id,
        product_name,
        category,
        sub_category,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(sales), 2) AS total_revenue,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
        DENSE_RANK() OVER (ORDER BY SUM(profit) DESC) AS profit_rank
    FROM retailpulse_orders
    GROUP BY product_id, product_name, category, sub_category
)
SELECT 
    profit_rank,
    product_name,
    category,
    sub_category,
    total_units_sold,
    total_revenue,
    total_profit,
    profit_margin_pct
FROM product_profit
WHERE profit_rank <= 10
ORDER BY profit_rank;

-- ----------------------------------------------------------------------------
-- 5. TOP 10 LARGEST LOSS-MAKING PRODUCTS (UNPROFITABLE SKUs)
-- ----------------------------------------------------------------------------
-- Business Question: Which products suffer the heaviest cumulative financial losses, 
-- and what are their average discount rates?

WITH product_losses AS (
    SELECT 
        product_id,
        product_name,
        category,
        sub_category,
        COUNT(row_id) AS times_ordered,
        SUM(quantity) AS units_sold,
        ROUND(SUM(sales), 2) AS total_revenue,
        ROUND(SUM(profit), 2) AS total_loss,
        ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
        ROUND(AVG(discount) * 100, 2) AS avg_discount_pct,
        DENSE_RANK() OVER (ORDER BY SUM(profit) ASC) AS loss_rank
    FROM retailpulse_orders
    GROUP BY product_id, product_name, category, sub_category
)
SELECT 
    loss_rank,
    product_name,
    category,
    sub_category,
    times_ordered,
    units_sold,
    total_revenue,
    total_loss,
    profit_margin_pct,
    avg_discount_pct
FROM product_losses
WHERE loss_rank <= 10
ORDER BY loss_rank;

-- ----------------------------------------------------------------------------
-- 6. DISCOUNT IMPACT BY PRODUCT CATEGORY
-- ----------------------------------------------------------------------------
-- Business Question: How does discounting affect margin compression across 
-- Furniture, Office Supplies, and Technology?

SELECT 
    category,
    discount_tier,
    COUNT(row_id) AS order_lines,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct
FROM retailpulse_orders
GROUP BY category, discount_tier
ORDER BY category, 
    CASE 
        WHEN discount_tier = '0% (No Discount)' THEN 1
        WHEN discount_tier = '1% - 20% (Low)' THEN 2
        WHEN discount_tier = '21% - 40% (Moderate)' THEN 3
        ELSE 4
    END;
