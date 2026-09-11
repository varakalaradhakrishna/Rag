"""
SQL Agent and Structured Data Retrieval Engine
Translates analytical business questions into verified SQLite SQL queries and extracts ground-truth facts.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, Optional
from database.database import query_sales_df, get_connection
from utils.logging import logger
from utils.helpers import format_currency, format_number, format_percentage

def execute_safe_analytical_query(query_text: str) -> Dict[str, Any]:
    """
    Parses natural language question, runs exact SQL aggregation, and returns verified facts.
    """
    q = query_text.lower()
    
    # 1. Total Revenue / Profit / Orders Overview
    if any(k in q for k in ["total revenue", "overall revenue", "how much revenue", "how much money"]):
        sql = "SELECT SUM(revenue) AS total_revenue, SUM(profit) AS total_profit, COUNT(*) AS total_orders, AVG(revenue) AS aov FROM sales;"
        df = query_sales_df(sql)
        rev = df["total_revenue"].iloc[0]
        prof = df["total_profit"].iloc[0]
        orders = df["total_orders"].iloc[0]
        aov = df["aov"].iloc[0]
        
        evidence = {
            "Total Revenue": format_currency(rev),
            "Total Net Profit": format_currency(prof),
            "Total Orders": format_number(orders),
            "Average Order Value (AOV)": format_currency(aov)
        }
        summary = f"Total historical revenue across all recorded transactions is **{format_currency(rev)}** across **{format_number(orders)}** orders with an Average Order Value of **{format_currency(aov)}**."
        return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # 2. Highest / Best Category
    if any(k in q for k in ["category", "highest revenue category", "top category", "best category", "which category"]):
        if "profit" in q:
            sql = "SELECT category, SUM(profit) AS total_profit, SUM(revenue) AS total_revenue, (SUM(profit)/SUM(revenue)*100) AS margin_pct FROM sales GROUP BY category ORDER BY total_profit DESC;"
            df = query_sales_df(sql)
            top_cat = df.iloc[0]
            evidence = {
                f"Top Category ({top_cat['category']}) Profit": format_currency(top_cat['total_profit']),
                "Profit Margin": format_percentage(top_cat['margin_pct']),
                "Total Category Revenue": format_currency(top_cat['total_revenue'])
            }
            summary = f"**{top_cat['category']}** generated the highest profit at **{format_currency(top_cat['total_profit'])}** with a **{top_cat['margin_pct']:.1f}%** profit margin."
            return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}
        else:
            sql = "SELECT category, SUM(revenue) AS total_revenue, SUM(quantity) AS units_sold, COUNT(*) AS orders FROM sales GROUP BY category ORDER BY total_revenue DESC;"
            df = query_sales_df(sql)
            top_cat = df.iloc[0]
            evidence = {
                f"Top Category ({top_cat['category']}) Revenue": format_currency(top_cat['total_revenue']),
                "Units Sold": format_number(top_cat['units_sold']),
                "Order Count": format_number(top_cat['orders'])
            }
            summary = f"**{top_cat['category']}** is the highest revenue-generating category, delivering **{format_currency(top_cat['total_revenue'])}** across **{format_number(top_cat['units_sold'])}** units sold."
            return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # 3. Top Product / Best Selling Product
    if any(k in q for k in ["product", "sold the most", "top product", "best selling", "most popular"]):
        sql = "SELECT product_name, category, brand, SUM(quantity) AS units_sold, SUM(revenue) AS total_revenue, AVG(rating) AS avg_rating FROM sales GROUP BY product_name ORDER BY total_revenue DESC LIMIT 5;"
        df = query_sales_df(sql)
        top_p = df.iloc[0]
        evidence = {
            "Top Product": top_p["product_name"],
            "Revenue": format_currency(top_p["total_revenue"]),
            "Units Sold": format_number(top_p["units_sold"]),
            "Customer Rating": f"{top_p['avg_rating']:.1f} / 5.0"
        }
        summary = f"The top performing product is **{top_p['product_name']}** ({top_p['brand']}), generating **{format_currency(top_p['total_revenue'])}** with **{format_number(top_p['units_sold'])}** units sold."
        return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # 4. Regional / State Analysis
    if any(k in q for k in ["state", "region", "city", "where do we sell", "geography"]):
        sql = "SELECT state, SUM(revenue) AS total_revenue, COUNT(*) AS orders, (CAST(SUM(return_flag) AS FLOAT)/COUNT(*)*100) AS return_rate FROM sales GROUP BY state ORDER BY total_revenue DESC LIMIT 5;"
        df = query_sales_df(sql)
        top_s = df.iloc[0]
        evidence = {
            "Top State": top_s["state"],
            "Revenue": format_currency(top_s["total_revenue"]),
            "Orders": format_number(top_s["orders"]),
            "Return Rate": format_percentage(top_s["return_rate"])
        }
        summary = f"**{top_s['state']}** leads all regions with **{format_currency(top_s['total_revenue'])}** in total sales and **{format_number(top_s['orders'])}** orders."
        return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # 5. Return Rate / Returns
    if any(k in q for k in ["return", "returns", "refund", "returned"]):
        sql = "SELECT (CAST(SUM(return_flag) AS FLOAT)/COUNT(*)*100) AS return_rate, SUM(return_flag) AS returned_units, COUNT(*) AS total_orders, SUM(CASE WHEN return_flag = 1 THEN revenue ELSE 0 END) AS returned_value FROM sales;"
        df = query_sales_df(sql)
        rate = df["return_rate"].iloc[0]
        ret_units = df["returned_units"].iloc[0]
        total = df["total_orders"].iloc[0]
        loss = df["returned_value"].iloc[0]
        evidence = {
            "Overall Return Rate": format_percentage(rate),
            "Returned Orders": f"{format_number(ret_units)} out of {format_number(total)}",
            "Gross Returned Value": format_currency(loss)
        }
        summary = f"The overall return rate is **{rate:.2f}%** ({format_number(ret_units)} returned orders), accounting for **{format_currency(loss)}** in reversed merchandise value."
        return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # 6. Average Order Value (AOV)
    if any(k in q for k in ["average order value", "aov", "average spend"]):
        sql = "SELECT AVG(revenue) AS aov, AVG(quantity) AS avg_qty, AVG(discount_percent) AS avg_disc FROM sales;"
        df = query_sales_df(sql)
        aov = df["aov"].iloc[0]
        evidence = {
            "Average Order Value": format_currency(aov),
            "Average Basket Quantity": f"{df['avg_qty'].iloc[0]:.2f} items",
            "Average Discount": format_percentage(df["avg_disc"].iloc[0])
        }
        summary = f"The current Average Order Value (AOV) is **{format_currency(aov)}**."
        return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # 7. Month Comparison (e.g. September vs October)
    if "compare" in q or ("september" in q and "october" in q) or "month" in q:
        sql = "SELECT month_name, year, COUNT(*) AS orders, SUM(revenue) AS revenue, SUM(profit) AS profit FROM sales GROUP BY year, month, month_name ORDER BY year, month;"
        df = query_sales_df(sql)
        evidence = {}
        for _, row in df.iterrows():
            evidence[f"{row['month_name']} {row['year']}"] = f"Revenue: {format_currency(row['revenue'])}, Orders: {format_number(row['orders'])}, Profit: {format_currency(row['profit'])}"
        summary = "Monthly performance comparison across recorded sales cycles."
        return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}

    # Fallback: General Summary
    sql = "SELECT COUNT(*) AS total_orders, SUM(revenue) AS total_rev, SUM(profit) AS total_prof, AVG(discount_percent) AS avg_disc FROM sales;"
    df = query_sales_df(sql)
    evidence = {
        "Total Orders": format_number(df["total_orders"].iloc[0]),
        "Total Revenue": format_currency(df["total_rev"].iloc[0]),
        "Total Profit": format_currency(df["total_prof"].iloc[0]),
        "Average Discount": format_percentage(df["avg_disc"].iloc[0])
    }
    summary = f"Database holds **{format_number(df['total_orders'].iloc[0])}** transactions totaling **{format_currency(df['total_rev'].iloc[0])}** in gross revenue."
    return {"success": True, "sql": sql, "evidence": evidence, "summary": summary, "df": df}
