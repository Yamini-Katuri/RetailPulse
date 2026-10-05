"""
================================================================================
RetailPulse — E-Commerce Sales & Customer Analytics
Script: python/eda.py
Purpose: Comprehensive Exploratory Data Analysis (EDA) & Portfolio Visualizations
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import seaborn as sns

# Set overall plotting aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9.5
plt.rcParams["axes.titlesize"] = 11.5
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 9.5
plt.rcParams["figure.titlesize"] = 13.5
plt.rcParams["figure.titleweight"] = "bold"

# Professional corporate palette
NAVY = "#0F172A"
BLUE = "#2563EB"
TEAL = "#0D9488"
GREEN = "#059669"
AMBER = "#D97706"
RED = "#DC2626"
PURPLE = "#7C3AED"
GRAY = "#475569"
LIGHT_GRAY = "#CBD5E1"
BG_COLOR = "#F8FAFC"
CARD_BG = "#FFFFFF"

def currency_fmt(x, pos):
    if abs(x) >= 1e6:
        return f"${x*1e-6:.2f}M"
    elif abs(x) >= 1e3:
        return f"${x*1e-3:.0f}K"
    else:
        return f"${x:.0f}"

def pct_fmt(x, pos):
    return f"{x:.0f}%"

def run_eda(cleaned_path: str, rfm_path: str, output_dir: str):
    print("=" * 80)
    print(" [1/6] LOADING PROCESSED DATASETS FOR EDA")
    print("=" * 80)

    df = pd.read_csv(cleaned_path)
    rfm = pd.read_csv(rfm_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["ship_date"] = pd.to_datetime(df["ship_date"])

    os.makedirs(output_dir, exist_ok=True)
    print(f" Loaded {len(df):,} cleaned transactions and {len(rfm):,} customer RFM profiles.")

    # --------------------------------------------------------------------------
    # CORE METRICS
    # --------------------------------------------------------------------------
    total_sales = df["sales"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    total_units = df["quantity"].sum()
    total_customers = df["customer_id"].nunique()
    overall_aov = total_sales / total_orders
    overall_margin = (total_profit / total_sales) * 100
    repeat_customers = (rfm["frequency_orders"] > 1).sum()
    repeat_rate = (repeat_customers / total_customers) * 100
    avg_shipping = df["shipping_days"].mean()
    loss_transactions = (df["profit"] < 0).sum()
    loss_rate = (loss_transactions / len(df)) * 100

    print("\n" + "=" * 80)
    print(" [2/6] CORE BUSINESS KPIs")
    print("=" * 80)
    print(f" Total Revenue:                ${total_sales:,.2f}")
    print(f" Total Net Profit:             ${total_profit:,.2f}")
    print(f" Overall Profit Margin:        {overall_margin:.2f}%")
    print(f" Total Distinct Orders:        {total_orders:,}")
    print(f" Total Units Sold:             {total_units:,}")
    print(f" Total Unique Customers:       {total_customers:,}")
    print(f" Repeat Customer Rate:         {repeat_rate:.2f}% ({repeat_customers}/{total_customers})")
    print(f" Average Order Value (AOV):    ${overall_aov:,.2f}")
    print(f" Average Shipping Duration:    {avg_shipping:.2f} days")
    print(f" Loss-Making Transactions:     {loss_rate:.2f}% ({loss_transactions:,}/{len(df):,})")

    # ==========================================================================
    # VISUALIZATION 1: EXECUTIVE OVERVIEW DASHBOARD
    # ==========================================================================
    print("\n" + "=" * 80)
    print(" [3/6] GENERATING DASHBOARD 1: EXECUTIVE OVERVIEW")
    print("=" * 80)

    fig = plt.figure(figsize=(16, 10), facecolor=BG_COLOR)
    gs = fig.add_gridspec(3, 3, height_ratios=[0.5, 1.2, 1.2], hspace=0.35, wspace=0.25)

    # Top Row: KPI Cards Header
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis("off")
    ax_kpi.set_facecolor(BG_COLOR)

    kpis = [
        ("TOTAL REVENUE", f"${total_sales:,.2f}", "+20.4% 2017 YoY", BLUE),
        ("NET PROFIT", f"${total_profit:,.2f}", f"{overall_margin:.1f}% Profit Margin", GREEN),
        ("TOTAL ORDERS", f"{total_orders:,}", f"{total_units:,} Units Sold", TEAL),
        ("UNIQUE CUSTOMERS", f"{total_customers:,}", f"{repeat_rate:.1f}% Repeat Buyers", PURPLE),
        ("AVG ORDER VALUE", f"${overall_aov:,.2f}", "Per Distinct Order", AMBER)
    ]

    for idx, (label, val, sub, col) in enumerate(kpis):
        x_start = 0.015 + idx * 0.198
        rect = patches.FancyBboxPatch(
            (x_start, 0.08), 0.185, 0.82,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            transform=ax_kpi.transAxes,
            facecolor="white", edgecolor="#E2E8F0", linewidth=1.5
        )
        ax_kpi.add_patch(rect)
        ax_kpi.text(x_start + 0.092, 0.70, label, transform=ax_kpi.transAxes,
                    ha="center", va="center", fontsize=8.5, fontweight="bold", color=GRAY)
        ax_kpi.text(x_start + 0.092, 0.42, val, transform=ax_kpi.transAxes,
                    ha="center", va="center", fontsize=12.5, fontweight="bold", color=col)
        ax_kpi.text(x_start + 0.092, 0.20, sub, transform=ax_kpi.transAxes,
                    ha="center", va="center", fontsize=7.5, color=GRAY)

    # Middle Left: Monthly Revenue & Profit Trend (2014 - 2017)
    ax_trend = fig.add_subplot(gs[1, :2])
    monthly = df.groupby("order_year_month").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index()

    ax_trend.plot(monthly.index, monthly["sales"], color=BLUE, linewidth=2.5, label="Monthly Revenue", marker="o", markersize=3)
    ax_trend.plot(monthly.index, monthly["profit"], color=GREEN, linewidth=2.0, label="Monthly Profit", linestyle="--")
    ax_trend.fill_between(monthly.index, monthly["profit"], color=GREEN, alpha=0.1)

    ax_trend.set_title("Monthly Revenue & Profit Growth (2014 – 2017)", pad=10)
    ax_trend.yaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    ax_trend.set_xticks(monthly.index[::6])
    ax_trend.set_xticklabels(monthly["order_year_month"].iloc[::6], rotation=0)
    ax_trend.set_ylabel("Amount ($)")
    ax_trend.legend(frameon=True, facecolor="white", loc="upper left")

    # Middle Right: Revenue & Profit Margin by Category
    ax_cat = fig.add_subplot(gs[1, 2])
    cat_df = df.groupby("category").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index()
    cat_df["margin"] = (cat_df["profit"] / cat_df["sales"]) * 100
    cat_df = cat_df.sort_values(by="sales", ascending=True)

    bars = ax_cat.barh(cat_df["category"], cat_df["sales"], color=[AMBER, TEAL, BLUE], height=0.55)
    ax_cat.set_title("Sales & Margin % by Category", pad=10)
    ax_cat.xaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    ax_cat.set_xlabel("Sales ($)")

    for bar, margin in zip(bars, cat_df["margin"]):
        w = bar.get_width()
        ax_cat.text(w * 0.5, bar.get_y() + bar.get_height()/2, f"${w/1e3:.0f}K ({margin:.1f}% Margin)",
                    va="center", ha="center", color="white", fontweight="bold", fontsize=8.5)

    # Bottom Left: Regional Sales & Profit Comparison
    ax_reg = fig.add_subplot(gs[2, 0])
    reg_df = df.groupby("region").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index().sort_values(by="sales", ascending=False)

    x = np.arange(len(reg_df))
    width = 0.35
    ax_reg.bar(x - width/2, reg_df["sales"], width, label="Sales", color=BLUE)
    ax_reg.bar(x + width/2, reg_df["profit"], width, label="Profit", color=GREEN)
    ax_reg.set_title("Sales & Profit by Region", pad=10)
    ax_reg.set_xticks(x)
    ax_reg.set_xticklabels(reg_df["region"])
    ax_reg.yaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    ax_reg.legend(frameon=True, facecolor="white")

    # Bottom Middle: Customer Segment Revenue Share (Doughnut)
    ax_seg = fig.add_subplot(gs[2, 1])
    seg_sales = df.groupby("segment")["sales"].sum()
    colors_seg = [BLUE, TEAL, PURPLE]
    wedges, texts, autotexts = ax_seg.pie(
        seg_sales, labels=seg_sales.index, autopct="%1.1f%%", startangle=140,
        colors=colors_seg, wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontweight("bold")
        at.set_fontsize(8.5)
    ax_seg.set_title("Sales by Customer Segment", pad=10)

    # Bottom Right: Shipping Mode Distribution & Delay Rate
    ax_ship = fig.add_subplot(gs[2, 2])
    ship_df = df.groupby("ship_mode").agg(
        orders=("order_id", "nunique"),
        avg_days=("shipping_days", "mean")
    ).reset_index().sort_values(by="orders", ascending=True)

    bars_ship = ax_ship.barh(ship_df["ship_mode"], ship_df["orders"], color=NAVY, height=0.55)
    ax_ship.set_title("Orders by Shipping Mode", pad=10)
    ax_ship.set_xlabel("Order Volume")
    for bar, days in zip(bars_ship, ship_df["avg_days"]):
        w = bar.get_width()
        ax_ship.text(w + 30, bar.get_y() + bar.get_height()/2, f"{w:,} ({days:.1f}d avg)",
                     va="center", ha="left", fontsize=8, color=NAVY)
    ax_ship.set_xlim(0, ship_df["orders"].max() * 1.3)

    plt.suptitle("RetailPulse — Executive Sales & Operations Overview", y=0.98, color=NAVY)
    exec_chart_path = os.path.join(output_dir, "executive_dashboard.png")
    plt.savefig(exec_chart_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f" Saved: {exec_chart_path}")

    # ==========================================================================
    # VISUALIZATION 2: SALES & PRODUCT DEEP DIVE DASHBOARD
    # ==========================================================================
    print("\n" + "=" * 80)
    print(" [4/6] GENERATING DASHBOARD 2: SALES & PRODUCT DEEP DIVE")
    print("=" * 80)

    fig, axs = plt.subplots(2, 2, figsize=(16, 10), facecolor=BG_COLOR)
    fig.subplots_adjust(hspace=0.32, wspace=0.25)

    # Top Left: Sub-Category Profitability Ranking & Margins
    subcat = df.groupby("sub_category").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index().sort_values(by="profit", ascending=True)
    subcat["margin"] = (subcat["profit"] / subcat["sales"]) * 100
    bar_colors = [RED if p < 0 else GREEN for p in subcat["profit"]]

    axs[0, 0].barh(subcat["sub_category"], subcat["profit"], color=bar_colors, height=0.6)
    axs[0, 0].axvline(0, color=GRAY, linewidth=1, linestyle="--")
    axs[0, 0].set_title("Sub-Category Net Profit Ranking (Loss vs. Profit Drivers)")
    axs[0, 0].xaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[0, 0].set_xlabel("Net Profit ($)")

    for _, row in subcat[subcat["profit"] < 0].iterrows():
        axs[0, 0].text(row["profit"] - 1500, row["sub_category"], f"${row['profit']/1e3:.1f}K",
                       va="center", ha="right", color=RED, fontweight="bold", fontsize=8)

    # Top Right: Discount vs. Profit Margin Collapse
    tier_perf = df.groupby("discount_tier").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "count"),
        loss_orders=("profit", lambda x: (x < 0).sum())
    ).reindex(["0% (No Discount)", "1% - 20% (Low)", "21% - 40% (Moderate)", "> 40% (Deep Discount)"]).reset_index()
    tier_perf["margin_pct"] = (tier_perf["profit"] / tier_perf["sales"]) * 100
    tier_perf["loss_rate"] = (tier_perf["loss_orders"] / tier_perf["orders"]) * 100

    x_tier = np.arange(len(tier_perf))
    axs[0, 1].bar(x_tier, tier_perf["margin_pct"], color=[GREEN, TEAL, AMBER, RED], width=0.55)
    axs[0, 1].axhline(0, color=GRAY, linewidth=1, linestyle="--")
    axs[0, 1].set_title("Profit Margin Collapse by Discount Tier (The Discount Trap)")
    axs[0, 1].set_xticks(x_tier)
    axs[0, 1].set_xticklabels(tier_perf["discount_tier"], rotation=10)
    axs[0, 1].set_ylabel("Profit Margin (%)")
    for i, row in tier_perf.iterrows():
        offset = 3 if row["margin_pct"] >= 0 else -6
        axs[0, 1].text(i, row["margin_pct"] + offset, f"{row['margin_pct']:.1f}%\n({row['loss_rate']:.0f}% loss)",
                       ha="center", va="center", fontsize=8.5, fontweight="bold",
                       color=NAVY if row["margin_pct"] >= 0 else RED)

    # Bottom Left: Top 10 Revenue Generating Products
    top_prod = df.groupby("product_name").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index().sort_values(by="sales", ascending=True).tail(10)
    top_prod["short_name"] = top_prod["product_name"].apply(lambda s: s[:30] + "..." if len(s) > 32 else s)

    axs[1, 0].barh(top_prod["short_name"], top_prod["sales"], color=BLUE, height=0.6)
    axs[1, 0].set_title("Top 10 Revenue-Generating Products")
    axs[1, 0].xaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[1, 0].set_xlabel("Sales ($)")

    # Bottom Right: Quarterly Seasonality Trend (Q1 - Q4 across years)
    quarterly = df.groupby(["order_year", "order_quarter"])["sales"].sum().unstack(level=0)
    for yr in quarterly.columns:
        axs[1, 1].plot(quarterly.index, quarterly[yr], marker="o", linewidth=2, label=f"Year {yr}")
    axs[1, 1].set_title("Quarterly Sales Seasonality (Q4 Demand Surge)")
    axs[1, 1].yaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[1, 1].set_xlabel("Quarter")
    axs[1, 1].set_ylabel("Sales ($)")
    axs[1, 1].legend(frameon=True, facecolor="white")

    plt.suptitle("RetailPulse — Sales & Product Performance Deep Dive", y=0.98, color=NAVY)
    sales_chart_path = os.path.join(output_dir, "sales_dashboard.png")
    plt.savefig(sales_chart_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f" Saved: {sales_chart_path}")

    # ==========================================================================
    # VISUALIZATION 3: CUSTOMER ANALYTICS & RFM DASHBOARD
    # ==========================================================================
    print("\n" + "=" * 80)
    print(" [5/6] GENERATING DASHBOARD 3: CUSTOMER ANALYTICS & RFM")
    print("=" * 80)

    fig, axs = plt.subplots(2, 2, figsize=(16, 10), facecolor=BG_COLOR)
    fig.subplots_adjust(hspace=0.32, wspace=0.25)

    # Top Left: Customer Count by RFM Segment
    seg_counts = rfm["customer_segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    seg_palette = {
        "Champions": GREEN,
        "Loyal Customers": BLUE,
        "Potential Loyalists": TEAL,
        "Promising / Needs Attention": PURPLE,
        "At Risk": AMBER,
        "Lost Customers": RED,
        "New Customers": "#38BDF8"
    }
    colors_c = [seg_palette.get(s, GRAY) for s in seg_counts["segment"]]

    axs[0, 0].barh(seg_counts["segment"], seg_counts["count"], color=colors_c, height=0.6)
    axs[0, 0].set_title("Customer Distribution by RFM Segment")
    axs[0, 0].set_xlabel("Number of Customers")
    for idx, row in seg_counts.iterrows():
        axs[0, 0].text(row["count"] + 3, row["segment"], f"{row['count']:,} ({row['count']/len(rfm)*100:.1f}%)",
                       va="center", ha="left", fontsize=8.5, color=NAVY)
    axs[0, 0].set_xlim(0, seg_counts["count"].max() * 1.25)

    # Top Right: Revenue Contribution by RFM Segment
    seg_rev = rfm.groupby("customer_segment")["monetary_sales"].sum().reset_index()
    seg_rev = seg_rev.sort_values(by="monetary_sales", ascending=True)
    colors_r = [seg_palette.get(s, GRAY) for s in seg_rev["customer_segment"]]

    axs[0, 1].barh(seg_rev["customer_segment"], seg_rev["monetary_sales"], color=colors_r, height=0.6)
    axs[0, 1].set_title("Total Revenue Contribution by RFM Segment")
    axs[0, 1].xaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[0, 1].set_xlabel("Revenue ($)")
    for idx, row in seg_rev.iterrows():
        pct = (row["monetary_sales"] / total_sales) * 100
        axs[0, 1].text(row["monetary_sales"] + 15000, row["customer_segment"], f"${row['monetary_sales']/1e3:.0f}K ({pct:.1f}%)",
                       va="center", ha="left", fontsize=8.5, color=NAVY)
    axs[0, 1].set_xlim(0, seg_rev["monetary_sales"].max() * 1.25)

    # Bottom Left: Recency vs. Monetary Scatter by Segment
    for seg_name, grp in rfm.groupby("customer_segment"):
        axs[1, 0].scatter(
            grp["recency_days"], grp["monetary_sales"],
            color=seg_palette.get(seg_name, GRAY),
            label=seg_name, alpha=0.65, edgecolors="none", s=grp["frequency_orders"] * 10
        )
    axs[1, 0].set_title("Customer Recency vs. Lifetime Spend (Bubble Size = Orders)")
    axs[1, 0].set_xlabel("Recency (Days Since Last Purchase)")
    axs[1, 0].set_ylabel("Monetary Spend ($)")
    axs[1, 0].yaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[1, 0].legend(frameon=True, facecolor="white", loc="upper right", fontsize=8)

    # Bottom Right: Top 10 High-Value VIP Customers
    top_cust = rfm.sort_values(by="monetary_sales", ascending=True).tail(10)
    axs[1, 1].barh(top_cust["customer_name"], top_cust["monetary_sales"], color=PURPLE, height=0.6)
    axs[1, 1].set_title("Top 10 High-Value VIP Customers")
    axs[1, 1].xaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[1, 1].set_xlabel("Lifetime Spend ($)")
    for _, row in top_cust.iterrows():
        axs[1, 1].text(row["monetary_sales"] + 200, row["customer_name"],
                       f"${row['monetary_sales']/1e3:.1f}K | {row['customer_segment']}",
                       va="center", ha="left", fontsize=7.5, color=NAVY)
    axs[1, 1].set_xlim(0, top_cust["monetary_sales"].max() * 1.35)

    plt.suptitle("RetailPulse — Customer Segmentation & RFM Analytics", y=0.98, color=NAVY)
    cust_chart_path = os.path.join(output_dir, "customer_dashboard.png")
    plt.savefig(cust_chart_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f" Saved: {cust_chart_path}")

    # ==========================================================================
    # VISUALIZATION 4: REGIONAL & OPERATIONS LOGISTICS DASHBOARD
    # ==========================================================================
    print("\n" + "=" * 80)
    print(" [6/6] GENERATING DASHBOARD 4: REGIONAL & OPERATIONS LOGISTICS")
    print("=" * 80)

    fig, axs = plt.subplots(2, 2, figsize=(16, 10), facecolor=BG_COLOR)
    fig.subplots_adjust(hspace=0.32, wspace=0.25)

    # Top Left: Top 10 States by Revenue & Profit
    state_df = df.groupby("state").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index().sort_values(by="sales", ascending=True).tail(10)

    axs[0, 0].barh(state_df["state"], state_df["sales"], color=BLUE, height=0.6, label="Sales")
    axs[0, 0].set_title("Top 10 States by Revenue")
    axs[0, 0].xaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axs[0, 0].set_xlabel("Sales ($)")
    for _, row in state_df.iterrows():
        axs[0, 0].text(row["sales"] + 5000, row["state"], f"${row['sales']/1e3:.0f}K (Prof: ${row['profit']/1e3:.1f}K)",
                       va="center", ha="left", fontsize=7.5, color=NAVY)
    axs[0, 0].set_xlim(0, state_df["sales"].max() * 1.35)

    # Top Right: Regional Profit Margin Comparison
    reg_margin = df.groupby("region").agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    ).reset_index()
    reg_margin["margin_pct"] = (reg_margin["profit"] / reg_margin["sales"]) * 100
    reg_margin = reg_margin.sort_values(by="margin_pct", ascending=True)

    bars_rm = axs[0, 1].barh(reg_margin["region"], reg_margin["margin_pct"], color=[AMBER, TEAL, GREEN, BLUE], height=0.55)
    axs[0, 1].set_title("Profit Margin Disparity Across Regions")
    axs[0, 1].set_xlabel("Profit Margin (%)")
    for bar in bars_rm:
        w = bar.get_width()
        axs[0, 1].text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.2f}%",
                       va="center", ha="left", fontsize=9, fontweight="bold", color=NAVY)
    axs[0, 1].set_xlim(0, reg_margin["margin_pct"].max() * 1.25)

    # Bottom Left: Average Shipping Duration by Shipping Mode
    ship_mode_summary = df.groupby("ship_mode").agg(
        avg_days=("shipping_days", "mean"),
        max_days=("shipping_days", "max"),
        delayed_rate=("is_shipping_delayed", lambda x: x.mean() * 100)
    ).reset_index().sort_values(by="avg_days", ascending=False)

    axs[1, 0].bar(ship_mode_summary["ship_mode"], ship_mode_summary["avg_days"], color=TEAL, width=0.5)
    axs[1, 0].set_title("Average Delivery Time by Shipping Mode (Days)")
    axs[1, 0].set_ylabel("Average Days to Ship")
    for idx, row in ship_mode_summary.iterrows():
        axs[1, 0].text(idx, row["avg_days"] + 0.15, f"{row['avg_days']:.1f} days\n({row['delayed_rate']:.0f}% delayed)",
                       ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=NAVY)
    axs[1, 0].set_ylim(0, 6.2)

    # Bottom Right: Order Volume Distribution by Day of Week
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_df = df.groupby("order_day_of_week")["order_id"].nunique().reindex(day_order).reset_index()
    axs[1, 1].plot(dow_df["order_day_of_week"], dow_df["order_id"], marker="s", color=PURPLE, linewidth=2.5)
    axs[1, 1].fill_between(range(len(dow_df)), dow_df["order_id"], color=PURPLE, alpha=0.15)
    axs[1, 1].set_title("Order Volume Distribution by Day of Week")
    axs[1, 1].set_ylabel("Distinct Orders")
    axs[1, 1].set_xticks(range(len(dow_df)))
    axs[1, 1].set_xticklabels(dow_df["order_day_of_week"], rotation=15)

    plt.suptitle("RetailPulse — Regional Performance & Operations Logistics", y=0.98, color=NAVY)
    reg_chart_path = os.path.join(output_dir, "regional_operations_dashboard.png")
    plt.savefig(reg_chart_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f" Saved: {reg_chart_path}")

    print("\n All 4 EDA dashboards generated successfully!")
    print("=" * 80)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_path = os.path.join(base_dir, "data", "processed", "retailpulse_cleaned.csv")
    rfm_path = os.path.join(base_dir, "data", "processed", "retailpulse_customer_rfm.csv")
    output_dir = os.path.join(base_dir, "screenshots")

    run_eda(cleaned_path, rfm_path, output_dir)
