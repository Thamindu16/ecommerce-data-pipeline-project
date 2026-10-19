-- =========================================================================
-- E-COMMERCE DATA PLATFORM - SQL ANALYTICS & INSIGHTS
-- =========================================================================

-- =========================================================================
-- PART 1: BASIC BUSINESS KPIs & METRICS
-- =========================================================================

-- 1. Top 5 Product Categories by Revenue
SELECT 
    p.product_category_name AS category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(pay.payment_value)::numeric, 2) AS total_revenue
FROM 
    orders o
JOIN 
    order_items oi ON o.order_id = oi.order_id
JOIN 
    products p ON oi.product_id = p.product_id
JOIN 
    order_payments pay ON o.order_id = pay.order_id
WHERE 
    o.order_status = 'delivered'
GROUP BY 
    p.product_category_name
ORDER BY 
    total_revenue DESC
LIMIT 5;


-- 2. Monthly Revenue & Order Trend
SELECT 
    TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(pay.payment_value)::numeric, 2) AS monthly_revenue
FROM 
    orders o
JOIN 
    order_payments pay ON o.order_id = pay.order_id
WHERE 
    o.order_status = 'delivered'
GROUP BY 
    TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')
ORDER BY 
    year_month ASC;


-- 3. Delivery Performance Breakdown (On-Time vs Late Delivery)
SELECT 
    CASE 
        WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 'On-Time / Early'
        ELSE 'Late Delivery'
    END AS delivery_status,
    COUNT(order_id) AS total_orders,
    ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER (), 2) AS percentage
FROM 
    orders
WHERE 
    order_status = 'delivered'
    AND order_delivered_customer_date IS NOT NULL
GROUP BY 
    delivery_status;



-- =========================================================================
-- PART 2: ADVANCED ANALYTICS (CTEs & WINDOW FUNCTIONS)
-- =========================================================================

-- 4. Cumulative Revenue (Running Total) using CTE & SUM() OVER ()
WITH MonthlySales AS (
    SELECT 
        TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
        ROUND(SUM(pay.payment_value)::numeric, 2) AS monthly_revenue
    FROM 
        orders o
    JOIN 
        order_payments pay ON o.order_id = pay.order_id
    WHERE 
        o.order_status = 'delivered'
    GROUP BY 
        TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')
)
SELECT 
    year_month,
    monthly_revenue,
    SUM(monthly_revenue) OVER (ORDER BY year_month) AS running_total_revenue
FROM 
    MonthlySales
ORDER BY 
    year_month;


-- 5. Top Seller in Each Category using DENSE_RANK()
WITH SellerCategoryRevenue AS (
    SELECT 
        p.product_category_name AS category,
        oi.seller_id,
        ROUND(SUM(pay.payment_value)::numeric, 2) AS total_sales,
        DENSE_RANK() OVER (
            PARTITION BY p.product_category_name 
            ORDER BY SUM(pay.payment_value) DESC
        ) AS rank
    FROM 
        order_items oi
    JOIN 
        products p ON oi.product_id = p.product_id
    JOIN 
        order_payments pay ON oi.order_id = pay.order_id
    GROUP BY 
        p.product_category_name, oi.seller_id
)
SELECT 
    category,
    seller_id,
    total_sales
FROM 
    SellerCategoryRevenue
WHERE 
    rank = 1 AND category IS NOT NULL
ORDER BY 
    total_sales DESC
LIMIT 10;


-- 6. Repeat Customer Identification using ROW_NUMBER()
WITH CustomerOrders AS (
    SELECT 
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id 
            ORDER BY o.order_purchase_timestamp
        ) AS order_sequence
    FROM 
        orders o
    JOIN 
        customers c ON o.customer_id = c.customer_id
    WHERE 
        o.order_status = 'delivered'
)
SELECT 
    customer_unique_id,
    COUNT(order_id) AS total_orders,
    MAX(order_sequence) AS highest_sequence
FROM 
    CustomerOrders
GROUP BY 
    customer_unique_id
HAVING 
    COUNT(order_id) > 1
ORDER BY 
    total_orders DESC
LIMIT 10;