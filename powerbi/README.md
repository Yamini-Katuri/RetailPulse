# Power BI Dashboard Architecture & Implementation Guide

This guide provides the complete blueprint for reproducing the 4-page interactive **RetailPulse Power BI Dashboard** in Power BI Desktop.

---

## 1. Data Model Architecture (Star Schema)

To adhere to Power BI best practices, the data model is configured in a high-performance **Star Schema** with one central Fact Table and four Dimension Tables.

```
                  ┌──────────────────────┐
                  │       Dim_Date       │
                  │  (Date Table / CAL)  │
                  └──────────┬───────────┘
                             │ 1
                             │
                             │ * (1:Many on order_date)
                             ▼
┌──────────────────┐    ┌───────────────────────────┐    ┌────────────────────┐
│   Dim_Customer   │ 1  │     Fact_SalesOrders      │  1 │    Dim_Product     │
│  (Customer_RFM)  ├───►│   (retailpulse_orders)    │◄───┤ (Product Hierarchy)│
└──────────────────┘ *  └─────────────┬─────────────┘ *  └────────────────────┘
                             ▲
                             │ * (1:Many)
                             │ 1
                  ┌──────────┴───────────┐
                  │     Dim_Geography    │
                  │ (Region/State/City)  │
                  └──────────────────────┘
```

### Table Relationships & Cardinality:
1. **`Dim_Date[Date]` (1) ───► `Fact_SalesOrders[order_date]` (*)** (Single direction)
2. **`Dim_Customer[customer_id]` (1) ───► `Fact_SalesOrders[customer_id]` (*)** (Single direction)
3. **`Dim_Product[product_id]` (1) ───► `Fact_SalesOrders[product_id]` (*)** (Single direction)
4. **`Dim_Geography[postal_code]` (1) ───► `Fact_SalesOrders[postal_code]` (*)** (Single direction)

---

## 2. Power Query Data Loading & Transformations

1. **Import Data**:
   - In Power BI Desktop, select **Get Data** ➔ **Text/CSV**.
   - Select `data/processed/retailpulse_cleaned.csv`.
   - Select `data/processed/retailpulse_customer_rfm.csv`.

2. **Generate Date Dimension (`Dim_Date`) via DAX**:
   Go to **Modeling** ➔ **New Table** and paste:
   ```dax
   Dim_Date = 
   VAR _MinDate = DATE(2014, 1, 1)
   VAR _MaxDate = DATE(2017, 12, 31)
   RETURN
   ADDCOLUMNS(
       CALENDAR(_MinDate, _MaxDate),
       "Year", YEAR([Date]),
       "Year-Quarter", FORMAT([Date], "YYYY") & "-Q" & FORMAT([Date], "Q"),
       "Quarter", "Q" & FORMAT([Date], "Q"),
       "Month Number", MONTH([Date]),
       "Month Name", FORMAT([Date], "MMM"),
       "Year-Month", FORMAT([Date], "YYYY-MM"),
       "Month-Year Sort", YEAR([Date]) * 100 + MONTH([Date]),
       "Day of Week", FORMAT([Date], "dddd"),
       "Day Number", WEEKDAY([Date], 2),
       "Is Weekend", IF(WEEKDAY([Date], 2) IN {6, 7}, "Weekend", "Weekday")
   )
   ```
   *Note: Mark `Dim_Date` as Date Table and sort `Month Name` by `Month Number`, and `Year-Month` by `Month-Year Sort`.*

3. **Create Dedicated Measures Table**:
   - Click **Enter Data**, name the table `_Measures`, create a dummy column, and load.
   - Add all DAX measures from `powerbi/dax_measures.dax` into `_Measures`.
   - Delete the dummy column so `_Measures` displays a calculator icon at the top of the field list.

---

## 3. Visual Styling & Color System

- **Background Canvas**: `#F8FAFC` (Off-white / Slate 50)
- **Visual Card Background**: `#FFFFFF` with 1px border `#E2E8F0` and subtle drop shadow
- **Primary Color (Revenue)**: `#2563EB` (Royal Blue)
- **Secondary Color (Profit)**: `#059669` (Emerald Green)
- **Accent Color (Operations / Orders)**: `#0D9488` (Teal)
- **Alert / Loss Color**: `#DC2626` (Crimson Red)
- **VIP / Customer Color**: `#7C3AED` (Violet Purple)
- **Text Primary**: `#0F172A` (Slate 900)
- **Text Secondary / Subtitles**: `#64748B` (Slate 500)
- **Font Family**: `Segoe UI` or `Inter` across all visuals

---

## 4. Page-by-Page Dashboard Layout

### 📊 Page 1 — Executive Overview
**Objective**: High-level strategic overview for executive stakeholders.

- **Header Banner**: Project title `RetailPulse — Executive Sales & Operations Overview`, data refresh tag, and logo.
- **Top Filter Slicers**:
  - `Dim_Date[Year]` (Tile / Dropdown)
  - `Fact_SalesOrders[region]` (Dropdown)
  - `Fact_SalesOrders[category]` (Dropdown)
  - `Fact_SalesOrders[segment]` (Dropdown)
- **KPI Card Row (Top)**:
  1. `[Total Revenue]` ($2.30M) with sub-label `+20.4% YoY Growth`
  2. `[Total Profit]` ($286.40K) with sub-label `12.47% Gross Margin`
  3. `[Total Distinct Orders]` (5,009) with sub-label `37,873 Units Sold`
  4. `[Total Unique Customers]` (793) with sub-label `98.5% Repeat Rate`
  5. `[Average Order Value (AOV)]` ($458.61) with sub-label `Per Distinct Order`
- **Visuals**:
  - **Visual 1 (Area/Line Chart)**: `Monthly Revenue & Profit Growth (2014 – 2017)` (X-axis: `Dim_Date[Year-Month]`, Y-axis: `[Total Revenue]`, `[Total Profit]`).
  - **Visual 2 (Horizontal Clustered Bar)**: `Sales by Category & Margin %` (Y-axis: `category`, X-axis: `[Total Revenue]`, Tooltip: `[Overall Profit Margin %]`).
  - **Visual 3 (Clustered Column Chart)**: `Sales & Profit by Region` (X-axis: `region`, Y-axis: `[Total Revenue]`, `[Total Profit]`).
  - **Visual 4 (Donut Chart)**: `Sales by Customer Segment` (Legend: `segment`, Values: `[Total Revenue]`).
  - **Visual 5 (Horizontal Bar)**: `Orders by Shipping Mode` (Y-axis: `ship_mode`, X-axis: `[Total Distinct Orders]`, Data Labels: Avg Shipping Days).

---

### 🛍️ Page 2 — Sales & Product Analysis
**Objective**: Diagnose product profitability, SKU-level performance, and discounting risks.

- **KPI Cards**:
  - `[Total Revenue]`, `[Overall Profit Margin %]`, `[Total Units Sold]`, `[Average Discount %]`, `[Loss Transaction Rate %]`.
- **Visuals**:
  - **Visual 1 (Diverging Horizontal Bar)**: `Sub-Category Net Profit Ranking` (Y-axis: `sub_category`, X-axis: `[Total Profit]`; conditional formatting: Red if `<0`, Green if `>0`). Highlights -$17.7K loss in Tables and -$3.5K in Bookcases.
  - **Visual 2 (Column Chart)**: `The Discount Trap: Profit Margin Collapse by Discount Tier` (X-axis: `discount_tier`, Y-axis: `[Overall Profit Margin %]`).
  - **Visual 3 (Horizontal Bar)**: `Top 10 Revenue-Generating Products` (Top 10 filter by `[Total Revenue]`).
  - **Visual 4 (Multi-Line Chart)**: `Quarterly Sales Seasonality (Q1 - Q4)` (X-axis: `Dim_Date[Quarter]`, Legend: `Dim_Date[Year]`, Y-axis: `[Total Revenue]`).
  - **Visual 5 (Matrix Table)**: Product drill-down (`category` ➔ `sub_category` ➔ `product_name`) with Sales, Profit, Margin %, and Loss Flag.

---

### 👥 Page 3 — Customer Analytics & RFM Segmentation
**Objective**: Uncover customer value cohorts, retention dynamics, and high-risk churn groups.

- **KPI Cards**:
  - `[Total Unique Customers]`, `[Repeat Customer Rate %]`, `[Average Customer Lifetime Spend]`, `[VIP Revenue Contribution %]`.
- **Visuals**:
  - **Visual 1 (Horizontal Bar)**: `Customer Distribution by RFM Segment` (Y-axis: `customer_segment`, X-axis: `[Total Unique Customers]`).
  - **Visual 2 (Horizontal Bar)**: `Total Revenue Contribution by RFM Segment` (Y-axis: `customer_segment`, X-axis: `[Total Revenue]`).
  - **Visual 3 (Scatter / Bubble Plot)**: `Customer Recency vs. Lifetime Monetary Spend` (X-axis: `recency_days`, Y-axis: `monetary_sales`, Size: `frequency_orders`, Color: `customer_segment`).
  - **Visual 4 (Table Visual)**: `Top 10 High-Value VIP Customers` (Columns: `Customer Name`, `Segment`, `Total Orders`, `Lifetime Spend`, `Lifetime Profit`, `Margin %`, `RFM Segment`).
  - **Visual 5 (Table Visual)**: `At-Risk Customers Intervention List` (Filtered to `RFM Segment = At Risk` and `Lifetime Spend > $2,500`).

---

### 🚚 Page 4 — Regional & Operations Logistics
**Objective**: Monitor logistics cycle times, regional delivery SLAs, and territorial margins.

- **KPI Cards**:
  - `[Average Shipping Days]`, `[Total Delayed Orders]`, `[Shipping Delay Rate %]`, `[Central Region Profit Margin %]`.
- **Visuals**:
  - **Visual 1 (Horizontal Bar / Map)**: `Top 10 States by Sales & Profit` (Y-axis: `state`, X-axis: `[Total Revenue]`, Data Labels: Sales & Profit).
  - **Visual 2 (Horizontal Bar)**: `Profit Margin Disparity Across Regions` (Y-axis: `region`, X-axis: `[Overall Profit Margin %]`).
  - **Visual 3 (Column Chart)**: `Average Delivery Time & Delay Rate by Shipping Mode` (X-axis: `ship_mode`, Y-axis: `[Average Shipping Days]`, Line Y-axis: `[Shipping Delay Rate %]`).
  - **Visual 4 (Line / Area Chart)**: `Order Volume by Day of Week` (X-axis: `Dim_Date[Day of Week]`, Y-axis: `[Total Distinct Orders]`).

---

## 5. Summary of Visual Deliverables

The repository includes high-resolution dashboard screenshots in `screenshots/`:
- `screenshots/executive_dashboard.png`
- `screenshots/sales_dashboard.png`
- `screenshots/customer_dashboard.png`
- `screenshots/regional_operations_dashboard.png`
