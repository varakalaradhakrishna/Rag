"""
Reusable SQL Queries for E-Commerce Sales Analytics
Demonstrates robust SQL analytical queries using aggregation, window functions, and filtering.
"""

SQL_OVERALL_KPIS = """
SELECT 
    COUNT(order_id) AS total_orders,
    COALESCE(SUM(revenue), 0) AS total_revenue,
    COALESCE(SUM(profit), 0) AS total_profit,
    COALESCE(SUM(quantity), 0) AS total_quantity,
    COALESCE(AVG(revenue), 0) AS avg_order_value,
    COALESCE(AVG(discount_percent), 0) AS avg_discount,
    COALESCE(AVG(rating), 0) AS avg_rating,
    COALESCE(AVG(delivery_days), 0) AS avg_delivery_days,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate_percent,
    (COALESCE(SUM(profit), 0) / NULLIF(SUM(revenue), 0)) * 100.0 AS overall_profit_margin
FROM sales;
"""

SQL_MONTHLY_PERFORMANCE = """
SELECT 
    year,
    month,
    month_name,
    COUNT(order_id) AS orders,
    SUM(quantity) AS units_sold,
    SUM(revenue) AS monthly_revenue,
    SUM(profit) AS monthly_profit,
    (SUM(profit) / NULLIF(SUM(revenue), 0)) * 100.0 AS profit_margin,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate
FROM sales
GROUP BY year, month, month_name
ORDER BY year ASC, month ASC;
"""

SQL_CATEGORY_PERFORMANCE = """
SELECT 
    category,
    COUNT(order_id) AS orders,
    SUM(quantity) AS units_sold,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(discount_percent) AS avg_discount,
    AVG(rating) AS avg_rating,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate,
    (SUM(profit) / NULLIF(SUM(revenue), 0)) * 100.0 AS profit_margin
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;
"""

SQL_TOP_PRODUCTS = """
SELECT 
    product_id,
    product_name,
    category,
    brand,
    COUNT(order_id) AS order_count,
    SUM(quantity) AS units_sold,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(rating) AS avg_rating,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate
FROM sales
GROUP BY product_id, product_name, category, brand
ORDER BY total_revenue DESC
LIMIT 15;
"""

SQL_WORST_PRODUCTS = """
SELECT 
    product_id,
    product_name,
    category,
    brand,
    COUNT(order_id) AS order_count,
    SUM(quantity) AS units_sold,
    SUM(revenue) AS total_revenue,
    SUM(profit) AS total_profit,
    AVG(rating) AS avg_rating,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate
FROM sales
GROUP BY product_id, product_name, category, brand
ORDER BY total_revenue ASC
LIMIT 10;
"""

SQL_STATE_PERFORMANCE = """
SELECT 
    state,
    COUNT(order_id) AS order_count,
    SUM(revenue) AS state_revenue,
    SUM(profit) AS state_profit,
    SUM(quantity) AS units_sold,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate
FROM sales
GROUP BY state
ORDER BY state_revenue DESC;
"""

SQL_CUSTOMER_RFM = """
SELECT 
    customer_id,
    MAX(order_date) AS last_order_date,
    COUNT(order_id) AS frequency,
    SUM(revenue) AS monetary_value,
    AVG(revenue) AS avg_spend,
    SUM(profit) AS total_profit_generated
FROM sales
GROUP BY customer_id
ORDER BY monetary_value DESC;
"""

SQL_RETURN_BREAKDOWN = """
SELECT 
    category,
    COUNT(order_id) AS total_orders,
    SUM(return_flag) AS returned_orders,
    (CAST(SUM(return_flag) AS FLOAT) / NULLIF(COUNT(order_id), 0)) * 100.0 AS return_rate,
    SUM(CASE WHEN return_flag = 1 THEN revenue ELSE 0 END) AS returned_revenue_loss
FROM sales
GROUP BY category
ORDER BY return_rate DESC;
"""
