WITH dates AS (
    SELECT
        dd::date as month
    FROM generate_series(
        '2020-10-01'::DATE
        ,NOW()
        ,'1 month'::interval
    ) dd
)
, products AS (
    SELECT
        sku,
        description as name,
        month
    FROM
        public.operations_product p
        JOIN public.operations_product_code pcode ON p.product_code_id = pcode.id
        JOIN dates ON 0=0
    WHERE
        (pcode.family = %(family)s OR %(family)s = 'All Products')

)
, detail AS (
    SELECT
        products.name,
        DATE_PART('YEAR', products.month) || '-' || LPAD(DATE_PART('MONTH', products.month)::TEXT, 2, '0') as month,
        SUM(COALESCE(so.quantity, 0)) as quantity_sold,
        SUM(COALESCE(so.net_sales, 0)) as total_sales,
        SUM(COALESCE(so.total_cost, 0)) as total_cost,
        SUM(COALESCE(so.net_sales, 0) - COALESCE(so.total_cost, 0)) as total_margin
    FROM
        products 
        LEFT JOIN report_moondance.sales_orders so ON 
            products.sku = so.product_sku AND
            products.month = so.processed_period
    GROUP BY
        products.name,
        products.month
    ORDER BY
        1,2
)
, summary AS (
    SELECT
        name,
        SUM(quantity_sold) as total_quantity,
        AVG(quantity_sold) as average_quantity,
        SUM(total_sales) as total_sales,
        SUM(total_cost) as total_cost,
        SUM(total_margin) as total_margin,
        ARRAY_AGG(month) as xaxis,
        ARRAY_AGG(quantity_sold) as phased_quantity,
        ARRAY_AGG(total_sales) as phased_sales,
        ARRAY_AGG(total_cost) as phased_cost,
        ARRAY_AGG(total_margin) as phased_margin
    FROM
        detail
    GROUP BY
        name
    HAVING
        SUM(COALESCE(quantity_sold, 0)) <> 0
    ORDER BY
        4 DESC
)
SELECT
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'name', name,
            'xaxis', xaxis,
            'total_quantity', total_quantity,
            'average_quantity', average_quantity,
            'total_sales', total_sales,
            'total_cost', total_cost,
            'total_margin', total_margin,
            'phased_quantity', phased_quantity,
            'phased_sales', phased_sales,
            'phased_cost', phased_cost,
            'phased_margin', phased_margin
        )
    )::TEXT as json
FROM
    summary
;
