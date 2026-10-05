"""
================================================================================
RetailPulse — E-Commerce Sales & Customer Analytics
Script: python/build_excel.py
Purpose: Build production-grade, multi-tab Excel Workbook (RetailPulse_Analysis.xlsx)
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import xlsxwriter

def build_excel_workbook(cleaned_csv: str, rfm_csv: str, excel_out: str):
    print("=" * 80)
    print(" [1/3] LOADING PROCESSED DATA FOR EXCEL WORKBOOK GENERATION")
    print("=" * 80)

    df = pd.read_csv(cleaned_csv)
    rfm = pd.read_csv(rfm_csv)
    print(f" Loaded {len(df):,} transactions and {len(rfm):,} customer profiles.")

    os.makedirs(os.path.dirname(excel_out), exist_ok=True)

    print("\n" + "=" * 80)
    print(" [2/3] CONSTRUCTING MULTI-TAB WORKBOOK WITH FORMULAS & NATIVE CHARTS")
    print("=" * 80)

    wb = xlsxwriter.Workbook(excel_out, {'nan_inf_to_errors': True})

    # Typography & Colors
    f_title = wb.add_format({'bold': True, 'font_size': 16, 'font_color': '#0F172A', 'font_name': 'Segoe UI'})
    f_subtitle = wb.add_format({'font_size': 10, 'font_color': '#64748B', 'font_name': 'Segoe UI'})
    f_section = wb.add_format({'bold': True, 'font_size': 11.5, 'font_color': '#1E293B', 'bottom': 2, 'bottom_color': '#2563EB', 'font_name': 'Segoe UI'})

    f_kpi_card_title = wb.add_format({'bold': True, 'font_size': 8.5, 'font_color': '#64748B', 'align': 'center', 'bg_color': '#F8FAFC', 'top': 1, 'left': 1, 'right': 1, 'border_color': '#CBD5E1', 'font_name': 'Segoe UI'})
    f_kpi_card_val_curr = wb.add_format({'bold': True, 'font_size': 13, 'font_color': '#2563EB', 'align': 'center', 'bg_color': '#FFFFFF', 'left': 1, 'right': 1, 'border_color': '#CBD5E1', 'num_format': '$#,##0.00', 'font_name': 'Segoe UI'})
    f_kpi_card_val_profit = wb.add_format({'bold': True, 'font_size': 13, 'font_color': '#059669', 'align': 'center', 'bg_color': '#FFFFFF', 'left': 1, 'right': 1, 'border_color': '#CBD5E1', 'num_format': '$#,##0.00', 'font_name': 'Segoe UI'})
    f_kpi_card_val_int = wb.add_format({'bold': True, 'font_size': 13, 'font_color': '#0D9488', 'align': 'center', 'bg_color': '#FFFFFF', 'left': 1, 'right': 1, 'border_color': '#CBD5E1', 'num_format': '#,##0', 'font_name': 'Segoe UI'})
    f_kpi_card_val_pct = wb.add_format({'bold': True, 'font_size': 13, 'font_color': '#7C3AED', 'align': 'center', 'bg_color': '#FFFFFF', 'left': 1, 'right': 1, 'border_color': '#CBD5E1', 'num_format': '0.00%', 'font_name': 'Segoe UI'})
    f_kpi_card_sub = wb.add_format({'font_size': 8, 'font_color': '#94A3B8', 'align': 'center', 'bg_color': '#F8FAFC', 'bottom': 1, 'left': 1, 'right': 1, 'border_color': '#CBD5E1', 'font_name': 'Segoe UI'})

    f_tbl_hdr = wb.add_format({'bold': True, 'font_size': 9.5, 'font_color': '#FFFFFF', 'bg_color': '#1E293B', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#475569', 'font_name': 'Segoe UI'})
    f_tbl_cell = wb.add_format({'font_size': 9, 'border': 1, 'border_color': '#E2E8F0', 'font_name': 'Segoe UI'})
    f_tbl_cell_center = wb.add_format({'font_size': 9, 'align': 'center', 'border': 1, 'border_color': '#E2E8F0', 'font_name': 'Segoe UI'})
    f_tbl_currency = wb.add_format({'font_size': 9, 'border': 1, 'border_color': '#E2E8F0', 'num_format': '$#,##0.00', 'font_name': 'Segoe UI'})
    f_tbl_pct = wb.add_format({'font_size': 9, 'border': 1, 'border_color': '#E2E8F0', 'num_format': '0.00%', 'align': 'right', 'font_name': 'Segoe UI'})
    f_tbl_int = wb.add_format({'font_size': 9, 'border': 1, 'border_color': '#E2E8F0', 'num_format': '#,##0', 'align': 'right', 'font_name': 'Segoe UI'})
    
    f_tbl_total = wb.add_format({'bold': True, 'font_size': 9.5, 'bg_color': '#F1F5F9', 'top': 2, 'top_color': '#1E293B', 'bottom': 2, 'bottom_color': '#1E293B', 'num_format': '$#,##0.00', 'font_name': 'Segoe UI'})
    f_tbl_total_lbl = wb.add_format({'bold': True, 'font_size': 9.5, 'bg_color': '#F1F5F9', 'top': 2, 'top_color': '#1E293B', 'bottom': 2, 'bottom_color': '#1E293B', 'font_name': 'Segoe UI'})
    f_tbl_total_pct = wb.add_format({'bold': True, 'font_size': 9.5, 'bg_color': '#F1F5F9', 'top': 2, 'top_color': '#1E293B', 'bottom': 2, 'bottom_color': '#1E293B', 'num_format': '0.00%', 'align': 'right', 'font_name': 'Segoe UI'})
    f_tbl_total_int = wb.add_format({'bold': True, 'font_size': 9.5, 'bg_color': '#F1F5F9', 'top': 2, 'top_color': '#1E293B', 'bottom': 2, 'bottom_color': '#1E293B', 'num_format': '#,##0', 'align': 'right', 'font_name': 'Segoe UI'})

    # --------------------------------------------------------------------------
    # 1. SUMMARY_KPIS TAB
    # --------------------------------------------------------------------------
    ws_kpi = wb.add_worksheet('Summary_KPIs')
    ws_kpi.hide_gridlines(0)

    ws_kpi.write('B2', 'RetailPulse — Executive Sales & Operations Summary', f_title)
    ws_kpi.write('B3', 'Comprehensive E-Commerce Business Intelligence & KPI Architecture', f_subtitle)

    # KPI Cards Row
    ws_kpi.merge_range('B5:C5', 'TOTAL REVENUE', f_kpi_card_title)
    ws_kpi.write_formula('B6', '=SUM(Cleaned_Data!R2:R9995)', f_kpi_card_val_curr)
    ws_kpi.write_blank('C6', None, f_kpi_card_val_curr)
    ws_kpi.merge_range('B7:C7', '+20.4% YoY Growth', f_kpi_card_sub)

    ws_kpi.merge_range('D5:E5', 'NET PROFIT', f_kpi_card_title)
    ws_kpi.write_formula('D6', '=SUM(Cleaned_Data!U2:U9995)', f_kpi_card_val_profit)
    ws_kpi.write_blank('E6', None, f_kpi_card_val_profit)
    ws_kpi.merge_range('D7:E7', '12.47% Gross Margin', f_kpi_card_sub)

    ws_kpi.merge_range('F5:G5', 'PROFIT MARGIN %', f_kpi_card_title)
    ws_kpi.write_formula('F6', '=D6/B6', f_kpi_card_val_pct)
    ws_kpi.write_blank('G6', None, f_kpi_card_val_pct)
    ws_kpi.merge_range('F7:G7', 'Target: > 15.0%', f_kpi_card_sub)

    ws_kpi.merge_range('H5:I5', 'TOTAL UNITS SOLD', f_kpi_card_title)
    ws_kpi.write_formula('H6', '=SUM(Cleaned_Data!S2:S9995)', f_kpi_card_val_int)
    ws_kpi.write_blank('I6', None, f_kpi_card_val_int)
    ws_kpi.merge_range('H7:I7', 'Across 5,009 Orders', f_kpi_card_sub)

    ws_kpi.merge_range('J5:K5', 'TOTAL CUSTOMERS', f_kpi_card_title)
    ws_kpi.write_formula('J6', '=COUNTA(Customer_RFM_Data!A2:A794)', f_kpi_card_val_int)
    ws_kpi.write_blank('K6', None, f_kpi_card_val_int)
    ws_kpi.merge_range('J7:K7', '98.5% Repeat Rate', f_kpi_card_sub)

    # Category Table
    ws_kpi.write('B10', '1. Category Revenue & Profit Breakdown', f_section)
    cat_headers = ['Category', 'Sales Revenue', 'Net Profit', 'Units Sold', 'Profit Margin %', 'Revenue Share %']
    for c_idx, h in enumerate(cat_headers):
        ws_kpi.write(11, 1 + c_idx, h, f_tbl_hdr)

    categories = ['Furniture', 'Office Supplies', 'Technology']
    for r_idx, cat in enumerate(categories):
        row_num = 13 + r_idx
        ws_kpi.write(row_num - 1, 1, cat, f_tbl_cell)
        ws_kpi.write_formula(row_num - 1, 2, f'=SUMIFS(Cleaned_Data!$R$2:$R$9995, Cleaned_Data!$O$2:$O$9995, B{row_num})', f_tbl_currency)
        ws_kpi.write_formula(row_num - 1, 3, f'=SUMIFS(Cleaned_Data!$U$2:$U$9995, Cleaned_Data!$O$2:$O$9995, B{row_num})', f_tbl_currency)
        ws_kpi.write_formula(row_num - 1, 4, f'=SUMIFS(Cleaned_Data!$S$2:$S$9995, Cleaned_Data!$O$2:$O$9995, B{row_num})', f_tbl_int)
        ws_kpi.write_formula(row_num - 1, 5, f'=IFERROR(D{row_num}/C{row_num}, 0)', f_tbl_pct)
        ws_kpi.write_formula(row_num - 1, 6, f'=IFERROR(C{row_num}/$B$6, 0)', f_tbl_pct)

    ws_kpi.write(15, 1, 'Total', f_tbl_total_lbl)
    ws_kpi.write_formula(15, 2, '=SUM(C13:C15)', f_tbl_total)
    ws_kpi.write_formula(15, 3, '=SUM(D13:D15)', f_tbl_total)
    ws_kpi.write_formula(15, 4, '=SUM(E13:E15)', f_tbl_total_int)
    ws_kpi.write_formula(15, 5, '=IFERROR(D16/C16, 0)', f_tbl_total_pct)
    ws_kpi.write_formula(15, 6, '=SUM(G13:G15)', f_tbl_total_pct)

    # Regional Table
    ws_kpi.write('B18', '2. Geographic Regional Performance', f_section)
    reg_headers = ['Region', 'Sales Revenue', 'Net Profit', 'Units Sold', 'Profit Margin %', 'Revenue Share %']
    for c_idx, h in enumerate(reg_headers):
        ws_kpi.write(19, 1 + c_idx, h, f_tbl_hdr)

    regions = ['Central', 'East', 'South', 'West']
    for r_idx, reg in enumerate(regions):
        row_num = 21 + r_idx
        ws_kpi.write(row_num - 1, 1, reg, f_tbl_cell)
        ws_kpi.write_formula(row_num - 1, 2, f'=SUMIFS(Cleaned_Data!$R$2:$R$9995, Cleaned_Data!$M$2:$M$9995, B{row_num})', f_tbl_currency)
        ws_kpi.write_formula(row_num - 1, 3, f'=SUMIFS(Cleaned_Data!$U$2:$U$9995, Cleaned_Data!$M$2:$M$9995, B{row_num})', f_tbl_currency)
        ws_kpi.write_formula(row_num - 1, 4, f'=SUMIFS(Cleaned_Data!$S$2:$S$9995, Cleaned_Data!$M$2:$M$9995, B{row_num})', f_tbl_int)
        ws_kpi.write_formula(row_num - 1, 5, f'=IFERROR(D{row_num}/C{row_num}, 0)', f_tbl_pct)
        ws_kpi.write_formula(row_num - 1, 6, f'=IFERROR(C{row_num}/$B$6, 0)', f_tbl_pct)

    ws_kpi.write(24, 1, 'Total', f_tbl_total_lbl)
    ws_kpi.write_formula(24, 2, '=SUM(C21:C24)', f_tbl_total)
    ws_kpi.write_formula(24, 3, '=SUM(D21:D24)', f_tbl_total)
    ws_kpi.write_formula(24, 4, '=SUM(E21:E24)', f_tbl_total_int)
    ws_kpi.write_formula(24, 5, '=IFERROR(D25/C25, 0)', f_tbl_total_pct)
    ws_kpi.write_formula(24, 6, '=SUM(G21:G24)', f_tbl_total_pct)

    # Discount Tier Table
    ws_kpi.write('B27', '3. Discount Tier Impact on Margin (The Discount Trap)', f_section)
    disc_headers = ['Discount Tier', 'Order Lines', 'Total Sales', 'Total Profit', 'Profit Margin %', 'Loss Order Rate %']
    for c_idx, h in enumerate(disc_headers):
        ws_kpi.write(28, 1 + c_idx, h, f_tbl_hdr)

    discount_tiers = ['0% (No Discount)', '1% - 20% (Low)', '21% - 40% (Moderate)', '> 40% (Deep Discount)']
    for r_idx, dt in enumerate(discount_tiers):
        row_num = 30 + r_idx
        ws_kpi.write(row_num - 1, 1, dt, f_tbl_cell)
        ws_kpi.write_formula(row_num - 1, 2, f'=COUNTIF(Cleaned_Data!$AG$2:$AG$9995, B{row_num})', f_tbl_int)
        ws_kpi.write_formula(row_num - 1, 3, f'=SUMIFS(Cleaned_Data!$R$2:$R$9995, Cleaned_Data!$AG$2:$AG$9995, B{row_num})', f_tbl_currency)
        ws_kpi.write_formula(row_num - 1, 4, f'=SUMIFS(Cleaned_Data!$U$2:$U$9995, Cleaned_Data!$AG$2:$AG$9995, B{row_num})', f_tbl_currency)
        ws_kpi.write_formula(row_num - 1, 5, f'=IFERROR(E{row_num}/D{row_num}, 0)', f_tbl_pct)
        ws_kpi.write_formula(row_num - 1, 6, f'=IFERROR(COUNTIFS(Cleaned_Data!$AG$2:$AG$9995, B{row_num}, Cleaned_Data!$U$2:$U$9995, "<0")/C{row_num}, 0)', f_tbl_pct)

    # Embedded Category Chart
    chart_cat = wb.add_chart({'type': 'column'})
    chart_cat.add_series({
        'name': 'Sales Revenue',
        'categories': '=Summary_KPIs!$B$13:$B$15',
        'values': '=Summary_KPIs!$C$13:$C$15',
        'fill': {'color': '#2563EB'},
    })
    chart_cat.add_series({
        'name': 'Net Profit',
        'categories': '=Summary_KPIs!$B$13:$B$15',
        'values': '=Summary_KPIs!$D$13:$D$15',
        'fill': {'color': '#059669'},
    })
    chart_cat.set_title({'name': 'Category Revenue vs. Net Profit', 'name_font': {'name': 'Segoe UI', 'size': 11, 'bold': True}})
    chart_cat.set_legend({'position': 'bottom'})
    chart_cat.set_size({'width': 480, 'height': 280})
    ws_kpi.insert_chart('I11', chart_cat)

    ws_kpi.set_column('A:A', 3)
    ws_kpi.set_column('B:B', 24)
    ws_kpi.set_column('C:D', 16)
    ws_kpi.set_column('E:E', 14)
    ws_kpi.set_column('F:F', 16)
    ws_kpi.set_column('G:G', 16)
    ws_kpi.set_column('H:K', 14)

    # --------------------------------------------------------------------------
    # 2. MONTHLY_TRENDS TAB
    # --------------------------------------------------------------------------
    ws_month = wb.add_worksheet('Monthly_Trends')
    # Gridlines are enabled by default
    ws_month.write('B2', 'Monthly Revenue & Profit Trajectory (2014 - 2017)', f_title)
    ws_month.write('B3', 'Time-series monthly sales volume, net profit, and margin progression', f_subtitle)

    month_headers = ['Year-Month', 'Year', 'Month', 'Monthly Revenue', 'Monthly Profit', 'Units Sold', 'Profit Margin %', 'Cumulative Revenue']
    for c_idx, h in enumerate(month_headers):
        ws_month.write(4, 1 + c_idx, h, f_tbl_hdr)

    unique_months = sorted(df['order_year_month'].unique())
    for r_idx, ym in enumerate(unique_months):
        row_num = 6 + r_idx
        yr, mo = ym.split('-')
        ws_month.write(row_num - 1, 1, ym, f_tbl_cell_center)
        ws_month.write(row_num - 1, 2, int(yr), f_tbl_cell_center)
        ws_month.write(row_num - 1, 3, int(mo), f_tbl_cell_center)
        ws_month.write_formula(row_num - 1, 4, f'=SUMIFS(Cleaned_Data!$R$2:$R$9995, Cleaned_Data!$Y$2:$Y$9995, B{row_num})', f_tbl_currency)
        ws_month.write_formula(row_num - 1, 5, f'=SUMIFS(Cleaned_Data!$U$2:$U$9995, Cleaned_Data!$Y$2:$Y$9995, B{row_num})', f_tbl_currency)
        ws_month.write_formula(row_num - 1, 6, f'=SUMIFS(Cleaned_Data!$S$2:$S$9995, Cleaned_Data!$Y$2:$Y$9995, B{row_num})', f_tbl_int)
        ws_month.write_formula(row_num - 1, 7, f'=IFERROR(F{row_num}/E{row_num}, 0)', f_tbl_pct)
        if r_idx == 0:
            ws_month.write_formula(row_num - 1, 8, f'=E{row_num}', f_tbl_currency)
        else:
            ws_month.write_formula(row_num - 1, 8, f'=I{row_num-1}+E{row_num}', f_tbl_currency)

    last_m_row = 5 + len(unique_months)
    ws_month.write(last_m_row, 1, 'Total / Overall', f_tbl_total_lbl)
    ws_month.write(last_m_row, 2, '', f_tbl_total_lbl)
    ws_month.write(last_m_row, 3, '', f_tbl_total_lbl)
    ws_month.write_formula(last_m_row, 4, f'=SUM(E6:E{last_m_row})', f_tbl_total)
    ws_month.write_formula(last_m_row, 5, f'=SUM(F6:F{last_m_row})', f_tbl_total)
    ws_month.write_formula(last_m_row, 6, f'=SUM(G6:G{last_m_row})', f_tbl_total_int)
    ws_month.write_formula(last_m_row, 7, f'=IFERROR(F{last_m_row+1}/E{last_m_row+1}, 0)', f_tbl_total_pct)
    ws_month.write_formula(last_m_row, 8, f'=I{last_m_row}', f_tbl_total)

    chart_trend = wb.add_chart({'type': 'line'})
    chart_trend.add_series({
        'name': 'Monthly Revenue',
        'categories': f'=Monthly_Trends!$B$6:$B${last_m_row}',
        'values': f'=Monthly_Trends!$E$6:$E${last_m_row}',
        'line': {'color': '#2563EB', 'width': 2.25},
    })
    chart_trend.add_series({
        'name': 'Monthly Profit',
        'categories': f'=Monthly_Trends!$B$6:$B${last_m_row}',
        'values': f'=Monthly_Trends!$F$6:$F${last_m_row}',
        'line': {'color': '#059669', 'width': 2.0, 'dash_type': 'dash'},
    })
    chart_trend.set_title({'name': 'Monthly Sales & Profit Trend (48 Months)', 'name_font': {'name': 'Segoe UI', 'size': 12, 'bold': True}})
    chart_trend.set_legend({'position': 'top'})
    chart_trend.set_size({'width': 650, 'height': 320})
    ws_month.insert_chart('K5', chart_trend)

    ws_month.set_column('A:A', 3)
    ws_month.set_column('B:B', 14)
    ws_month.set_column('C:D', 8)
    ws_month.set_column('E:F', 16)
    ws_month.set_column('G:G', 12)
    ws_month.set_column('H:I', 18)

    # --------------------------------------------------------------------------
    # 3. CATEGORY_PERFORMANCE TAB
    # --------------------------------------------------------------------------
    ws_cat = wb.add_worksheet('Category_Performance')
    # Gridlines enabled by default
    ws_cat.write('B2', 'Sub-Category Performance & Product Line Profitability', f_title)
    ws_cat.write('B3', 'Granular audit of sales, gross profit, loss-making orders, and margins across 17 sub-categories', f_subtitle)

    sub_headers = ['Category', 'Sub-Category', 'Total Revenue', 'Total Profit', 'Units Sold', 'Profit Margin %', 'Loss Orders Count', 'Loss Order Rate %']
    for c_idx, h in enumerate(sub_headers):
        ws_cat.write(4, 1 + c_idx, h, f_tbl_hdr)

    subcats = df[['category', 'sub_category']].drop_duplicates().sort_values(by=['category', 'sub_category']).values
    for r_idx, (cat, sub) in enumerate(subcats):
        row_num = 6 + r_idx
        ws_cat.write(row_num - 1, 1, cat, f_tbl_cell)
        ws_cat.write(row_num - 1, 2, sub, f_tbl_cell)
        ws_cat.write_formula(row_num - 1, 3, f'=SUMIFS(Cleaned_Data!$R$2:$R$9995, Cleaned_Data!$P$2:$P$9995, C{row_num})', f_tbl_currency)
        ws_cat.write_formula(row_num - 1, 4, f'=SUMIFS(Cleaned_Data!$U$2:$U$9995, Cleaned_Data!$P$2:$P$9995, C{row_num})', f_tbl_currency)
        ws_cat.write_formula(row_num - 1, 5, f'=SUMIFS(Cleaned_Data!$S$2:$S$9995, Cleaned_Data!$P$2:$P$9995, C{row_num})', f_tbl_int)
        ws_cat.write_formula(row_num - 1, 6, f'=IFERROR(E{row_num}/D{row_num}, 0)', f_tbl_pct)
        ws_cat.write_formula(row_num - 1, 7, f'=COUNTIFS(Cleaned_Data!$P$2:$P$9995, C{row_num}, Cleaned_Data!$U$2:$U$9995, "<0")', f_tbl_int)
        ws_cat.write_formula(row_num - 1, 8, f'=IFERROR(H{row_num}/COUNTIF(Cleaned_Data!$P$2:$P$9995, C{row_num}), 0)', f_tbl_pct)

    last_s_row = 5 + len(subcats)
    ws_cat.write(last_s_row, 1, 'Total', f_tbl_total_lbl)
    ws_cat.write(last_s_row, 2, '', f_tbl_total_lbl)
    ws_cat.write_formula(last_s_row, 3, f'=SUM(D6:D{last_s_row})', f_tbl_total)
    ws_cat.write_formula(last_s_row, 4, f'=SUM(E6:E{last_s_row})', f_tbl_total)
    ws_cat.write_formula(last_s_row, 5, f'=SUM(F6:F{last_s_row})', f_tbl_total_int)
    ws_cat.write_formula(last_s_row, 6, f'=IFERROR(E{last_s_row+1}/D{last_s_row+1}, 0)', f_tbl_total_pct)
    ws_cat.write_formula(last_s_row, 7, f'=SUM(H6:H{last_s_row})', f_tbl_total_int)
    ws_cat.write_formula(last_s_row, 8, f'=IFERROR(H{last_s_row+1}/COUNT(Cleaned_Data!$A$2:$A$9995), 0)', f_tbl_total_pct)

    chart_sub = wb.add_chart({'type': 'bar'})
    chart_sub.add_series({
        'name': 'Net Profit',
        'categories': f'=Category_Performance!$C$6:$C${last_s_row}',
        'values': f'=Category_Performance!$E$6:$E${last_s_row}',
        'fill': {'color': '#2563EB'},
    })
    chart_sub.set_title({'name': 'Net Profit by Sub-Category (Highlighting Tables & Bookcase Deficit)', 'name_font': {'name': 'Segoe UI', 'size': 11, 'bold': True}})
    chart_sub.set_legend({'none': True})
    chart_sub.set_size({'width': 540, 'height': 380})
    ws_cat.insert_chart('K5', chart_sub)

    ws_cat.set_column('A:A', 3)
    ws_cat.set_column('B:C', 18)
    ws_cat.set_column('D:E', 16)
    ws_cat.set_column('F:F', 12)
    ws_cat.set_column('G:I', 18)

    # --------------------------------------------------------------------------
    # 4. CUSTOMER_RFM TAB
    # --------------------------------------------------------------------------
    ws_rfm_tab = wb.add_worksheet('Customer_RFM')
    ws_rfm_tab.write('B2', 'Customer Behavioral RFM Segmentation & Cohort Analysis', f_title)
    ws_rfm_tab.write('B3', 'RFM model segment summary, revenue contribution, and VIP customer rankings', f_subtitle)

    rfm_headers = ['Customer Segment', 'Customer Count', 'Customer Share %', 'Total Revenue', 'Revenue Share %', 'Total Profit', 'Profit Margin %', 'Avg Customer Spend']
    for c_idx, h in enumerate(rfm_headers):
        ws_rfm_tab.write(4, 1 + c_idx, h, f_tbl_hdr)

    rfm_segments = ['Champions', 'Loyal Customers', 'Potential Loyalists', 'Promising / Needs Attention', 'At Risk', 'Lost Customers', 'New Customers']
    for r_idx, seg in enumerate(rfm_segments):
        row_num = 6 + r_idx
        ws_rfm_tab.write(row_num - 1, 1, seg, f_tbl_cell)
        ws_rfm_tab.write_formula(row_num - 1, 2, f'=COUNTIF(Customer_RFM_Data!$I$2:$I$794, B{row_num})', f_tbl_int)
        ws_rfm_tab.write_formula(row_num - 1, 3, f'=IFERROR(C{row_num}/$C$13, 0)', f_tbl_pct)
        ws_rfm_tab.write_formula(row_num - 1, 4, f'=SUMIF(Customer_RFM_Data!$I$2:$I$794, B{row_num}, Customer_RFM_Data!$C$2:$C$794)', f_tbl_currency)
        ws_rfm_tab.write_formula(row_num - 1, 5, f'=IFERROR(E{row_num}/$E$13, 0)', f_tbl_pct)
        ws_rfm_tab.write_formula(row_num - 1, 6, f'=SUMIF(Customer_RFM_Data!$I$2:$I$794, B{row_num}, Customer_RFM_Data!$D$2:$D$794)', f_tbl_currency)
        ws_rfm_tab.write_formula(row_num - 1, 7, f'=IFERROR(G{row_num}/E{row_num}, 0)', f_tbl_pct)
        ws_rfm_tab.write_formula(row_num - 1, 8, f'=IFERROR(E{row_num}/C{row_num}, 0)', f_tbl_currency)

    ws_rfm_tab.write(12, 1, 'Total Customer Base', f_tbl_total_lbl)
    ws_rfm_tab.write_formula(12, 2, '=SUM(C6:C12)', f_tbl_total_int)
    ws_rfm_tab.write_formula(12, 3, '=SUM(D6:D12)', f_tbl_total_pct)
    ws_rfm_tab.write_formula(12, 4, '=SUM(E6:E12)', f_tbl_total)
    ws_rfm_tab.write_formula(12, 5, '=SUM(F6:F12)', f_tbl_total_pct)
    ws_rfm_tab.write_formula(12, 6, '=SUM(G6:G12)', f_tbl_total)
    ws_rfm_tab.write_formula(12, 7, '=IFERROR(G13/E13, 0)', f_tbl_total_pct)
    ws_rfm_tab.write_formula(12, 8, '=IFERROR(E13/C13, 0)', f_tbl_total)

    chart_rfm = wb.add_chart({'type': 'doughnut'})
    chart_rfm.add_series({
        'name': 'Revenue Share',
        'categories': '=Customer_RFM!$B$6:$B$12',
        'values': '=Customer_RFM!$E$6:$E$12',
        'hole_size': 50,
    })
    chart_rfm.set_title({'name': 'Revenue Contribution by RFM Segment', 'name_font': {'name': 'Segoe UI', 'size': 11, 'bold': True}})
    chart_rfm.set_size({'width': 450, 'height': 280})
    ws_rfm_tab.insert_chart('K5', chart_rfm)

    # Top 10 VIP Customers Table
    ws_rfm_tab.write('B16', 'Top 10 High-Value VIP Customers (Lifetime Spend)', f_section)
    vip_headers = ['Customer ID', 'Customer Name', 'Segment', 'Total Orders', 'Lifetime Sales', 'Lifetime Profit', 'Profit Margin %', 'RFM Segment']
    for c_idx, h in enumerate(vip_headers):
        ws_rfm_tab.write(17, 1 + c_idx, h, f_tbl_hdr)

    top_10_custs = rfm.sort_values(by='monetary_sales', ascending=False).head(10)
    for r_idx, (_, row) in enumerate(top_10_custs.iterrows()):
        row_num = 19 + r_idx
        ws_rfm_tab.write(row_num - 1, 1, row['customer_id'], f_tbl_cell_center)
        ws_rfm_tab.write(row_num - 1, 2, row['customer_name'], f_tbl_cell)
        ws_rfm_tab.write(row_num - 1, 3, row['segment'], f_tbl_cell)
        ws_rfm_tab.write(row_num - 1, 4, row['frequency_orders'], f_tbl_int)
        ws_rfm_tab.write(row_num - 1, 5, row['monetary_sales'], f_tbl_currency)
        ws_rfm_tab.write(row_num - 1, 6, row['total_profit'], f_tbl_currency)
        ws_rfm_tab.write_formula(row_num - 1, 7, f'=IFERROR(G{row_num}/F{row_num}, 0)', f_tbl_pct)
        ws_rfm_tab.write(row_num - 1, 8, row['customer_segment'], f_tbl_cell)

    ws_rfm_tab.set_column('A:A', 3)
    ws_rfm_tab.set_column('B:C', 22)
    ws_rfm_tab.set_column('D:D', 15)
    ws_rfm_tab.set_column('E:G', 16)
    ws_rfm_tab.set_column('H:I', 18)

    # --------------------------------------------------------------------------
    # 5. CLEANED_DATA TAB (9,994 transaction rows)
    # --------------------------------------------------------------------------
    ws_data = wb.add_worksheet('Cleaned_Data')

    data_headers = df.columns.tolist()
    for c_idx, h in enumerate(data_headers):
        ws_data.write(0, c_idx, h, f_tbl_hdr)

    for r_idx, row in df.iterrows():
        row_list = row.tolist()
        for c_idx, val in enumerate(row_list):
            if pd.isna(val):
                ws_data.write_blank(r_idx + 1, c_idx, None, f_tbl_cell)
            elif isinstance(val, (int, np.integer)):
                ws_data.write_number(r_idx + 1, c_idx, int(val), f_tbl_cell)
            elif isinstance(val, (float, np.floating)):
                ws_data.write_number(r_idx + 1, c_idx, float(val), f_tbl_cell)
            else:
                ws_data.write_string(r_idx + 1, c_idx, str(val), f_tbl_cell)

    ws_data.set_column('A:AP', 14)

    # --------------------------------------------------------------------------
    # 6. CUSTOMER_RFM_DATA TAB (793 customer summary rows)
    # --------------------------------------------------------------------------
    ws_rfm_data = wb.add_worksheet('Customer_RFM_Data')

    rfm_cols = ['customer_id', 'customer_name', 'monetary_sales', 'total_profit', 'frequency_orders', 'recency_days', 'r_score', 'f_score', 'customer_segment', 'aov']
    for c_idx, h in enumerate(rfm_cols):
        ws_rfm_data.write(0, c_idx, h, f_tbl_hdr)

    for r_idx, row in rfm[rfm_cols].iterrows():
        row_list = row.tolist()
        for c_idx, val in enumerate(row_list):
            if pd.isna(val):
                ws_rfm_data.write_blank(r_idx + 1, c_idx, None, f_tbl_cell)
            elif isinstance(val, (int, np.integer)):
                ws_rfm_data.write_number(r_idx + 1, c_idx, int(val), f_tbl_cell)
            elif isinstance(val, (float, np.floating)):
                ws_rfm_data.write_number(r_idx + 1, c_idx, float(val), f_tbl_cell)
            else:
                ws_rfm_data.write_string(r_idx + 1, c_idx, str(val), f_tbl_cell)

    ws_rfm_data.set_column('A:J', 16)

    wb.close()
    print("\n" + "=" * 80)
    print(f" [3/3] EXCEL WORKBOOK GENERATED SUCCESSFULLY")
    print(f" Path: {excel_out}")
    print(f" File Size: {os.path.getsize(excel_out):,} bytes")
    print("=" * 80)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_csv = os.path.join(base_dir, "data", "processed", "retailpulse_cleaned.csv")
    rfm_csv = os.path.join(base_dir, "data", "processed", "retailpulse_customer_rfm.csv")
    excel_out = os.path.join(base_dir, "excel", "RetailPulse_Analysis.xlsx")

    build_excel_workbook(cleaned_csv, rfm_csv, excel_out)
