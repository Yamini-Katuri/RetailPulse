"""
================================================================================
RetailPulse — E-Commerce Sales & Customer Analytics
Script: python/data_cleaning.py
Purpose: Reproducible Data Cleaning, Validation & Feature Engineering Pipeline
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np

def run_cleaning_pipeline(raw_filepath: str, processed_filepath: str, rfm_filepath: str):
    """
    Executes the end-to-end data cleaning, validation, feature engineering,
    and RFM customer aggregation pipeline.
    """
    print("=" * 80)
    print(" [1/5] LOADING RAW DATASET")
    print(f" Source: {raw_filepath}")
    print("=" * 80)

    if not os.path.exists(raw_filepath):
        raise FileNotFoundError(f"Raw data file not found at: {raw_filepath}")

    # Load raw dataset with appropriate encoding
    df = pd.read_csv(raw_filepath, encoding="windows-1252")
    raw_rows, raw_cols = df.shape
    print(f" Loaded successfully: {raw_rows:,} rows across {raw_cols} columns.")

    print("\n" + "=" * 80)
    print(" [2/5] DATA AUDIT & STANDARDIZATION")
    print("=" * 80)

    # 1. Standardize column names to clean snake_case
    original_cols = df.columns.tolist()
    df.columns = [
        c.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        for c in df.columns
    ]
    print(f" Standardized {len(df.columns)} column names to snake_case:")
    print(f"   {df.columns.tolist()}")

    # 2. String trimming for all text columns
    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # 3. Check and report missing values
    missing_counts = df.isnull().sum()
    missing_report = missing_counts[missing_counts > 0]
    if len(missing_report) == 0:
        print(" Missing values check: 0 missing values detected across all columns.")
    else:
        print(f" Missing values detected:\n{missing_report}")

    # 4. Check and report duplicate records
    full_duplicates = df.duplicated().sum()
    print(f" Full duplicate rows: {full_duplicates}")
    print(f" Unique Row IDs: {df['row_id'].nunique():,} / {len(df):,}")
    print(f" Unique Order IDs: {df['order_id'].nunique():,}")
    print(f" Unique Customer IDs: {df['customer_id'].nunique():,}")
    print(f" Unique Product IDs: {df['product_id'].nunique():,}")

    # 5. Parse and validate date fields
    print("\n Parsing date fields ('order_date', 'ship_date')...")
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="mixed")

    # Validate chronological consistency (ship_date >= order_date)
    invalid_dates = df[df["ship_date"] < df["order_date"]]
    if len(invalid_dates) > 0:
        print(f" WARNING: Found {len(invalid_dates)} records with ship_date < order_date.")
    else:
        print(" Date integrity confirmed: All ship_date >= order_date (0 negative durations).")

    # 6. Format Postal Code as clean zero-padded string
    df["postal_code"] = df["postal_code"].astype(str).str.replace(".0", "", regex=False).str.zfill(5)

    print("\n" + "=" * 80)
    print(" [3/5] FEATURE ENGINEERING")
    print("=" * 80)

    # Date-derived temporal features
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["order_month_name"] = df["order_date"].dt.strftime("%b")
    df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["order_quarter"] = "Q" + df["order_date"].dt.quarter.astype(str)
    df["order_year_quarter"] = df["order_year"].astype(str) + "-Q" + df["order_date"].dt.quarter.astype(str)
    df["order_day_of_week"] = df["order_date"].dt.day_name()
    df["is_weekend"] = df["order_date"].dt.dayofweek.isin([5, 6]).astype(int)

    # Operational features
    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
    sla_map = {"Same Day": 0, "First Class": 2, "Second Class": 3, "Standard Class": 5}
    df["shipping_sla_days"] = df["ship_mode"].map(sla_map)
    df["is_shipping_delayed"] = (df["shipping_days"] > df["shipping_sla_days"]).astype(int)

    # Financial & Unit economics features
    df["unit_price"] = np.round(df["sales"] / df["quantity"], 2)
    df["cost"] = np.round(df["sales"] - df["profit"], 2)
    # Undiscounted gross revenue: sales / (1 - discount)
    df["gross_sales"] = np.where(
        df["discount"] < 1.0,
        np.round(df["sales"] / (1.0 - df["discount"]), 2),
        df["sales"]
    )
    df["discount_amount"] = np.round(df["gross_sales"] - df["sales"], 2)
    df["profit_margin_pct"] = np.round((df["profit"] / df["sales"]) * 100, 2)
    df["is_profitable"] = (df["profit"] > 0).astype(int)
    df["is_loss_making"] = (df["profit"] < 0).astype(int)

    # Categorize discount tiers
    def categorize_discount(disc):
        if disc == 0.0:
            return "0% (No Discount)"
        elif disc <= 0.20:
            return "1% - 20% (Low)"
        elif disc <= 0.40:
            return "21% - 40% (Moderate)"
        else:
            return "> 40% (Deep Discount)"

    df["discount_tier"] = df["discount"].apply(categorize_discount)

    print(f" Created {14} engineered features:")
    print("   Temporal: order_year, order_month, order_month_name, order_year_month,")
    print("             order_quarter, order_year_quarter, order_day_of_week, is_weekend")
    print("   Logistics: shipping_days, shipping_sla_days, is_shipping_delayed")
    print("   Financials: unit_price, cost, gross_sales, discount_amount,")
    print("               profit_margin_pct, is_profitable, is_loss_making, discount_tier")

    print("\n" + "=" * 80)
    print(" [4/5] CUSTOMER RFM AGGREGATION & SEGMENTATION")
    print("=" * 80)

    # Snapshot date for Recency calculation: Day after last recorded order
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)
    print(f" Reference Snapshot Date for RFM: {snapshot_date.strftime('%Y-%m-%d')}")

    # Aggregate customer metrics
    rfm = df.groupby(["customer_id", "customer_name", "segment"]).agg(
        recency_days=("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency_orders=("order_id", "nunique"),
        monetary_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_units=("quantity", "sum"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max")
    ).reset_index()

    # Derived customer metrics
    rfm["aov"] = np.round(rfm["monetary_sales"] / rfm["frequency_orders"], 2)
    rfm["customer_tenure_days"] = (snapshot_date - rfm["first_order_date"]).dt.days
    rfm["monetary_sales"] = np.round(rfm["monetary_sales"], 2)
    rfm["total_profit"] = np.round(rfm["total_profit"], 2)
    rfm["profit_margin_pct"] = np.round((rfm["total_profit"] / rfm["monetary_sales"]) * 100, 2)

    # RFM Scoring using 1-5 quantiles
    rfm["r_score"] = pd.qcut(rfm["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency_orders"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary_sales"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["rfm_cell"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
    rfm["rfm_index"] = np.round((rfm["r_score"] + rfm["f_score"] + rfm["m_score"]) / 3.0, 2)

    # Practical & explainable business segment classification
    def assign_rfm_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif f >= 4 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 3 and m >= 3:
            return "Potential Loyalists"
        elif r >= 4 and f <= 2 and m <= 2:
            return "New Customers"
        elif r <= 2 and (f >= 3 or m >= 3):
            return "At Risk"
        elif r <= 2 and f <= 2 and m <= 2:
            return "Lost Customers"
        else:
            return "Promising / Needs Attention"

    rfm["customer_segment"] = rfm.apply(assign_rfm_segment, axis=1)

    # Merge customer segment back into the cleaned transaction dataset
    df = df.merge(
        rfm[["customer_id", "customer_segment", "r_score", "f_score", "m_score", "rfm_cell"]],
        on="customer_id",
        how="left"
    )

    print(f" RFM Segmentation completed for {len(rfm):,} unique customers.")
    print("\n Customer Segment Breakdown:")
    segment_summary = rfm["customer_segment"].value_counts().reset_index()
    segment_summary.columns = ["Customer Segment", "Customer Count"]
    print(segment_summary.to_string(index=False))

    print("\n" + "=" * 80)
    print(" [5/5] SAVING PROCESSED ARTIFACTS")
    print("=" * 80)

    # Ensure output directories exist
    os.makedirs(os.path.dirname(processed_filepath), exist_ok=True)
    os.makedirs(os.path.dirname(rfm_filepath), exist_ok=True)

    # Save cleaned transactions
    df.to_csv(processed_filepath, index=False, encoding="utf-8")
    print(f" Cleaned transactions saved to: {processed_filepath}")
    print(f"   Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # Save customer RFM dataset
    rfm.to_csv(rfm_filepath, index=False, encoding="utf-8")
    print(f" Customer RFM dataset saved to: {rfm_filepath}")
    print(f"   Shape: {rfm.shape[0]:,} rows x {rfm.shape[1]} columns")

    print("\n Data cleaning & feature engineering pipeline completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "retailpulse_raw.csv")
    cleaned_path = os.path.join(base_dir, "data", "processed", "retailpulse_cleaned.csv")
    rfm_path = os.path.join(base_dir, "data", "processed", "retailpulse_customer_rfm.csv")

    run_cleaning_pipeline(raw_path, cleaned_path, rfm_path)
