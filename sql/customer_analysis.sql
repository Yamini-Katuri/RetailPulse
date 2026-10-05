-- ============================================================================
-- RetailPulse — E-Commerce Sales & Customer Analytics
-- Script: sql/customer_analysis.sql
-- Database Engine: MySQL 8.0+ / ANSI SQL Compatible
-- Purpose: Customer Lifetime Value, Repeat Analysis, SQL RFM Segmentation & Churn Risk
-- ============================================================================

USE retailpulse_db;

-- ----------------------------------------------------------------------------
-- 1. OVERALL CUSTOMER BASE METRICS & REPEAT PURCHASE RATE
-- ----------------------------------------------------------------------------
-- Business Question: How many total unique customers exist, what is the repeat 
-- buyer rate, and what is the average customer lifetime value?

WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(sales) AS customer_revenue,
        SUM(profit) AS customer_profit
    FROM retailpulse_orders
    GROUP BY customer_id
)
SELECT 
    COUNT(*) AS total_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND((SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS repeat_customer_rate_pct,
    ROUND(AVG(customer_revenue), 2) AS avg_customer_lifetime_revenue,
    ROUND(AVG(customer_profit), 2) AS avg_customer_lifetime_profit,
    ROUND(AVG(total_orders), 2) AS avg_orders_per_customer
FROM customer_order_counts;

-- ----------------------------------------------------------------------------
-- 2. TOP 10 HIGHEST-VALUE VIP CUSTOMERS
-- ----------------------------------------------------------------------------
-- Business Question: Who are our top 10 most valuable individual customers by 
-- total revenue generated, and how profitable are they?

SELECT 
    customer_id,
    customer_name,
    segment,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_purchased,
    ROUND(SUM(sales), 2) AS total_lifetime_sales,
    ROUND(SUM(profit), 2) AS total_lifetime_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value_aov
FROM retailpulse_orders
GROUP BY customer_id, customer_name, segment
ORDER BY total_lifetime_sales DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 3. CUSTOMER ORDER FREQUENCY DISTRIBUTION
-- ----------------------------------------------------------------------------
-- Business Question: How is the customer base distributed across order frequency tiers?

WITH customer_freq AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(sales) AS total_spend
    FROM retailpulse_orders
    GROUP BY customer_id
),
frequency_buckets AS (
    SELECT 
        customer_id,
        total_spend,
        CASE 
            WHEN order_count = 1 THEN '1 Order (One-Time Buyer)'
            WHEN order_count BETWEEN 2 AND 4 THEN '2 - 4 Orders (Occasional)'
            WHEN order_count BETWEEN 5 AND 8 THEN '5 - 8 Orders (Frequent)'
            ELSE '9+ Orders (Power Buyer)'
        END AS frequency_tier
    FROM customer_freq
)
SELECT 
    frequency_tier,
    COUNT(*) AS customer_count,
    ROUND((COUNT(*) / (SELECT COUNT(*) FROM customer_freq)) * 100, 2) AS customer_share_pct,
    ROUND(SUM(total_spend), 2) AS total_revenue_generated,
    ROUND((SUM(total_spend) / (SELECT SUM(total_spend) FROM customer_freq)) * 100, 2) AS revenue_share_pct,
    ROUND(AVG(total_spend), 2) AS avg_spend_per_customer
FROM frequency_buckets
GROUP BY frequency_tier
ORDER BY total_revenue_generated DESC;

-- ----------------------------------------------------------------------------
-- 4. END-TO-END RFM SEGMENTATION IN PURE SQL (CTEs + NTILE + CASE WHEN)
-- ----------------------------------------------------------------------------
-- Business Question: How do we categorize customers into behavioral segments 
-- (Champions, Loyal, At-Risk, Lost) natively in SQL?

WITH rfm_raw AS (
    SELECT 
        customer_id,
        customer_name,
        segment AS customer_type,
        -- Recency: Days between max transaction date and customer's last order
        DATEDIFF('2017-12-31', MAX(order_date)) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency_orders,
        ROUND(SUM(sales), 2) AS monetary_spend,
        ROUND(SUM(profit), 2) AS total_profit
    FROM retailpulse_orders
    GROUP BY customer_id, customer_name, segment
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        customer_type,
        recency_days,
        frequency_orders,
        monetary_spend,
        total_profit,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_spend ASC) AS m_score
    FROM rfm_raw
),
rfm_segmented AS (
    SELECT 
        customer_id,
        customer_name,
        customer_type,
        recency_days,
        frequency_orders,
        monetary_spend,
        total_profit,
        r_score,
        f_score,
        m_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 4 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 3 AND m_score >= 3 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score <= 2 AND m_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND (f_score >= 3 OR m_score >= 3) THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost Customers'
            ELSE 'Promising / Needs Attention'
        END AS rfm_segment
    FROM rfm_scores
)
SELECT 
    rfm_segment,
    COUNT(*) AS customer_count,
    ROUND((COUNT(*) / (SELECT COUNT(*) FROM rfm_segmented)) * 100, 2) AS customer_share_pct,
    ROUND(SUM(monetary_spend), 2) AS segment_revenue,
    ROUND((SUM(monetary_spend) / (SELECT SUM(monetary_spend) FROM rfm_segmented)) * 100, 2) AS revenue_share_pct,
    ROUND(SUM(total_profit), 2) AS segment_profit,
    ROUND((SUM(total_profit) / SUM(monetary_spend)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency_orders), 1) AS avg_order_count,
    ROUND(AVG(monetary_spend), 2) AS avg_customer_spend
FROM rfm_segmented
GROUP BY rfm_segment
ORDER BY segment_revenue DESC;

-- ----------------------------------------------------------------------------
-- 5. AT-RISK HIGH-VALUE CUSTOMERS (CHURN INTERVENTION LIST)
-- ----------------------------------------------------------------------------
-- Business Question: Which historically high-spending customers have not ordered 
-- in the last 180+ days and require proactive retention outreach?

WITH customer_activity AS (
    SELECT 
        customer_id,
        customer_name,
        segment,
        DATEDIFF('2017-12-31', MAX(order_date)) AS days_since_last_order,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(sales), 2) AS lifetime_spend,
        ROUND(SUM(profit), 2) AS lifetime_profit
    FROM retailpulse_orders
    GROUP BY customer_id, customer_name, segment
)
SELECT 
    customer_id,
    customer_name,
    segment,
    days_since_last_order,
    total_orders,
    lifetime_spend,
    lifetime_profit
FROM customer_activity
WHERE days_since_last_order >= 180 AND lifetime_spend >= 2500
ORDER BY lifetime_spend DESC;
