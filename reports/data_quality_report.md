# RetailPulse — Data Quality & Integrity Assessment Report

**Project**: RetailPulse — E-Commerce Sales & Customer Analytics  
**Pipeline**: `python/data_cleaning.py`  
**Dataset Reference**: Tableau Sample Superstore Public Retail Repository  

---

## 1. Executive Summary & Quality Scorecard

| Metric | Raw Dataset | Cleaned Dataset | Customer RFM Dataset | Status / Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Row Count** | 9,994 | 9,994 | 793 | 100% record retention (0 dropped rows) |
| **Column Count** | 21 | 45 | 19 | Standardized + 24 engineered/RFM features |
| **Missing Values** | 0 | 0 | 0 | 100% completeness across all core fields |
| **Duplicate Rows** | 0 | 0 | 0 | Verified unique transaction line items |
| **Chronological Integrity** | 100% | 100% | 100% | 0 negative durations (`ship_date >= order_date`) |
| **Date Coverage** | 2014-01-03 to 2017-12-30 | 2014-01-03 to 2017-12-30 | Snapshot: 2017-12-31 | 48 complete calendar months (4 full years) |

---

## 2. Raw Dataset Profiling & Initial Ingestion Audit

The raw dataset was ingested from the verified canonical repository (`data/raw/retailpulse_raw.csv`).

### Initial Column Inventory & Data Types
| Original Column | Raw Type | Detected Anomalies / Formatting Needs |
| :--- | :---: | :--- |
| `Row ID` | `int64` | Primary key identifier (1 to 9,994). |
| `Order ID` | `object` | Alphanumeric formatted as `CA-2016-152156` (5,009 unique). |
| `Order Date` | `object` | Mixed date strings (`MM-DD-YYYY` and `MM/DD/YYYY`). |
| `Ship Date` | `object` | Mixed date strings (`MM-DD-YYYY` and `MM/DD/YYYY`). |
| `Ship Mode` | `object` | 4 categorical classes: Standard Class, Second Class, First Class, Same Day. |
| `Customer ID` | `object` | Alphanumeric formatted as `CG-12520` (793 unique). |
| `Customer Name` | `object` | String (793 unique customer names). |
| `Segment` | `object` | 3 categories: Consumer, Corporate, Home Office. |
| `Country` | `object` | Uniformly 'United States'. |
| `City` | `object` | 531 unique US cities. |
| `State` | `object` | 49 unique US states. |
| `Postal Code` | `int64` | Numeric format requiring zero-padding for 5-digit US postal codes. |
| `Region` | `object` | 4 geographic territories: West, East, Central, South. |
| `Product ID` | `object` | Alphanumeric product SKUs (1,862 unique). |
| `Category` | `object` | 3 broad categories: Furniture, Office Supplies, Technology. |
| `Sub-Category` | `object` | 17 sub-categories. |
| `Product Name` | `object` | Free-text product titles (1,850 unique). |
| `Sales` | `float64` | Range: $0.44 to $22,638.48. |
| `Quantity` | `int64` | Range: 1 to 14 units. |
| `Discount` | `float64` | Range: 0.00 (0%) to 0.80 (80%). |
| `Profit` | `float64` | Range: -$6,599.98 to +$8,399.98 (negative values represent transaction losses). |

---

## 3. Data Cleaning & Standardization Decisions

### Decision 1: Column Naming Convention
- **Action**: Converted all column headers from PascalCase / Spaced format (e.g., `Order Date`, `Sub-Category`, `Ship Mode`) to standardized lowercase `snake_case` (`order_date`, `sub_category`, `ship_mode`).
- **Rationale**: Ensures seamless compatibility across Python, Pandas, MySQL 8+, and Power Query without requiring escaped identifier quotes.

### Decision 2: Date Ingestion & Chronology Validation
- **Action**: Converted `order_date` and `ship_date` to `datetime64[ns]` using `pd.to_datetime(..., format='mixed')`.
- **Validation**:
  - Minimum Order Date: `2014-01-03`
  - Maximum Order Date: `2017-12-30`
  - Computed `shipping_days = (ship_date - order_date).dt.days`
  - Tested for negative durations: **0 records found** where `ship_date < order_date`.
  - Duration Range: 0 to 7 days (Mean: 3.96 days).

### Decision 3: Text Trimming & Categorical Normalization
- **Action**: Applied `.str.strip()` across all string columns (`customer_name`, `product_name`, `city`, `state`, `sub_category`) to remove leading and trailing whitespace.
- **Rationale**: Prevents phantom duplicate categories caused by invisible trailing spaces during SQL `GROUP BY` and Power BI dimension lookups.

### Decision 4: Postal Code Standardization
- **Action**: Converted integer postal codes to 5-character zero-padded strings (`.astype(str).str.zfill(5)`).
- **Rationale**: Preserves leading zeroes for East Coast US zip codes (e.g., `01841` instead of `1841`).

---

## 4. Feature Engineering Data Dictionary

All derived features were calculated strictly from existing fields without fabricating artificial data:

| Feature Name | Data Type | Formula / Logic | Business Purpose |
| :--- | :---: | :--- | :--- |
| `order_year` | `int64` | `YEAR(order_date)` | Multi-year trend & YoY analysis |
| `order_month` | `int64` | `MONTH(order_date)` | Monthly seasonality profiling |
| `order_month_name` | `object` | `FORMAT(order_date, 'MMM')` | Visual chart labeling |
| `order_year_month` | `object` | `FORMAT(order_date, 'YYYY-MM')` | Continuous time-series aggregation |
| `order_quarter` | `object` | `'Q' + QUARTER(order_date)` | Quarterly seasonality analysis |
| `order_year_quarter` | `object` | `'YYYY-Q' + QUARTER(order_date)` | Multi-year quarterly trend analysis |
| `order_day_of_week` | `object` | `DAYNAME(order_date)` | Day-of-week order volume distribution |
| `is_weekend` | `int64` | `1 if day in (Sat, Sun) else 0` | Weekend vs. weekday purchasing patterns |
| `shipping_days` | `int64` | `DATEDIFF(ship_date, order_date)` | Logistics fulfillment duration |
| `shipping_sla_days` | `int64` | Same Day: 0, First: 2, Second: 3, Std: 5 | Benchmark SLA per shipping tier |
| `is_shipping_delayed`| `int64` | `1 if shipping_days > sla_days else 0` | SLA breach rate tracking |
| `unit_price` | `float64` | `sales / quantity` | Price per unit realized |
| `cost` | `float64` | `sales - profit` | Estimated product cost of goods |
| `gross_sales` | `float64` | `sales / (1 - discount)` when discount < 1 | Pre-discount list price revenue |
| `discount_amount` | `float64` | `gross_sales - sales` | Dollar value of discounts granted |
| `profit_margin_pct` | `float64` | `(profit / sales) * 100` | Line-item gross margin % |
| `is_profitable` | `int64` | `1 if profit > 0 else 0` | Transaction profitability flag |
| `is_loss_making` | `int64` | `1 if profit < 0 else 0` | Loss-making transaction flag |
| `discount_tier` | `object` | `0%`, `1-20%`, `21-40%`, `>40%` | Discount elasticity analysis |
| `customer_segment` | `object` | RFM Segment (Champions, Loyal, At Risk, etc.) | Behavioral customer segmentation |

---

## 5. Customer RFM Table Data Dictionary (`retailpulse_customer_rfm.csv`)

| Column Name | Data Type | Description | Source / Derived |
| :--- | :---: | :--- | :---: |
| `customer_id` | `object` | Unique alphanumeric customer key | Source |
| `customer_name` | `object` | Customer full name | Source |
| `segment` | `object` | Business segment (Consumer, Corporate, Home Office) | Source |
| `recency_days` | `int64` | Days between 2017-12-31 and customer's latest order | Derived |
| `frequency_orders` | `int64` | Total distinct orders placed (`COUNT(DISTINCT order_id)`) | Derived |
| `monetary_sales` | `float64` | Cumulative customer lifetime revenue (`SUM(sales)`) | Derived |
| `total_profit` | `float64` | Cumulative customer lifetime profit (`SUM(profit)`) | Derived |
| `total_units` | `int64` | Cumulative items purchased (`SUM(quantity)`) | Derived |
| `first_order_date`| `object` | Earliest recorded order date | Derived |
| `last_order_date` | `object` | Most recent recorded order date | Derived |
| `aov` | `float64` | Average Order Value (`monetary_sales / frequency_orders`) | Derived |
| `customer_tenure_days`| `int64` | Days between first order and snapshot date | Derived |
| `profit_margin_pct`| `float64` | Customer net margin % (`total_profit / monetary_sales * 100`)| Derived |
| `r_score` | `int64` | 1–5 Recency Quintile score | Derived |
| `f_score` | `int64` | 1–5 Frequency Quintile score | Derived |
| `m_score` | `int64` | 1–5 Monetary Quintile score | Derived |
| `rfm_cell` | `object` | Concatenated score (e.g. `'555'`, `'111'`) | Derived |
| `rfm_index` | `float64` | Average of R, F, and M scores | Derived |
| `customer_segment`| `object` | Categorical classification (Champions, Loyal, At Risk, etc.) | Derived |

---

## 6. Dataset Limitations & Analytical Boundaries

To uphold academic and professional integrity, the following dataset limitations are explicitly noted:

1. **Absence of Return / Cancellation Reason Codes**: While line items record return transactions through negative profits or returns mapping, granular cancellation reason codes (e.g., "damaged packaging", "buyer remorse") are not present in the public dataset.
2. **Attribution & Marketing Channel**: The dataset does not track web marketing touchpoints (e.g., Google Ads, Organic SEO, Email Referral). Customer acquisition is modeled strictly through transactional cohort tenure.
3. **Inventory Holding & Carrying Costs**: Cost is derived from `sales - profit` (representing COGS). Dynamic warehouse storage fees and inventory carrying costs are not recorded separately.
