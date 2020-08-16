WITH nexternal_shipping AS (
    WITH n AS (
        SELECT
            order_number,
            order_line,
            total_weight,
            shipping_rate
        FROM
            public.sales_orders_nexternal
    )
    , d AS (
        SELECT
            order_number,
            SUM(total_weight) AS total_weight
        FROM
            public.sales_orders_nexternal
        GROUP BY
            order_number
        HAVING
            SUM(total_weight) <> 0
    )

    SELECT
        n.order_number,
        n.order_line,
        ((n.total_weight::NUMERIC / d.total_weight::NUMERIC) * n.shipping_rate::NUMERIC)::NUMERIC(16, 2) as weighted_average_shipping,
        CASE
            WHEN d.total_weight <= 0.25 THEN '0oz - 4oz'
            WHEN d.total_weight <= 0.5 THEN '4oz - 8oz'
            WHEN d.total_weight <= 0.75 THEN '8oz - 12oz'
            WHEN d.total_weight <= 1 THEN '12oz - 16oz'
            WHEN d.total_weight <= 2 THEN '32oz - 48oz'
            ELSE '48oz+'
        END as weight_bucket
        
    FROM
        n
        JOIN d ON n.order_number = d.order_number        
)/*
, amazon_fees AS (
    WITH n AS (
        SELECT
            "order_id",
            "sku",
            SUM("product_sales") as total_sales,
            SUM("product_sales_tax") as product_sales_tax,
            SUM("shipping_credits") as shipping_credits,
            SUM("shipping_credits_tax") as shipping_credits_tax,
            SUM("giftwrap_credits") as giftwrap_credits,
            SUM("giftwrap_credits_tax") as giftwrap_credits_tax,
            SUM("promotional_rebates") as promotional_rebates,
            SUM("promotional_rebates_tax") as promotional_rebates_tax,
            SUM("marketplace_withheld_tax") as marketplace_withheld_tax,
            SUM("selling_fees") as selling_fees,
            SUM("fba_fees") as fba_fees,
            SUM("other_transaction_fees") as other_transaction_fees,
            SUM("other") as other,
            SUM("total") as total
        FROM
            "public"."fees_amazon"
        GROUP BY
            "order_id",
            "sku"
    )
    
)*/




SELECT
    'Nexternal'::TEXT as platform,
    so.order_status,
    so.order_number::VARCHAR as order_number,
    so.order_line,
    so.order_date,
    DATE_PART('YEAR', so.order_date)::INTEGER as order_year,
    DATE_PART('MONTH', so.order_date)::INTEGER as order_month,
    so.ship_date,
    so.customer_type,
    so.product_category as marketing_category,
    COALESCE(item_master_nexternal.supply_chain_category, no_sku.supply_chain_category) as supply_chain_category,
    so.product_name as product_name_historical,
    item_master_nexternal.name as product_name_nexternal,
    (
        COALESCE(item_master_nexternal.supply_chain_name, no_sku.supply_chain_name) || 
        CASE WHEN item_master_nexternal.measure IS NOT NULL THEN ' ' || item_master_nexternal.measure::NUMERIC(16, 1)::TEXT ELSE '' END ||
        CASE WHEN item_master_nexternal.unit_of_measure IS NOT NULL THEN item_master_nexternal.unit_of_measure ELSE '' END 
    ) as supply_chain_name,
    so.product_sku as nexternal_sku,
    NULL::TEXT as amazon_asin,
    so.product_attribute,
    so.unit_price as unit_sale_price,
    (nexternal_shipping.weighted_average_shipping / CASE WHEN so.quantity = 0 THEN NULL ELSE so.quantity END)::NUMERIC(16, 2) as unit_cost_shipping,
    COALESCE((so.sales_tax_rate::NUMERIC/100::NUMERIC) * so.unit_price, 0)::NUMERIC(16, 2) as unit_cost_tax,
    (
         COALESCE(so.unit_price, 0)
        -COALESCE((nexternal_shipping.weighted_average_shipping / CASE WHEN so.quantity = 0 THEN NULL ELSE so.quantity END)::NUMERIC(16, 2), 0)
        -COALESCE((so.sales_tax_rate::NUMERIC/100::NUMERIC) * so.unit_price, 0)
    )::NUMERIC(16, 2) as unit_margin,
    so.quantity,
    so.extended_price as total_sales,
    nexternal_shipping.weighted_average_shipping as total_cost_shipping,
    ((so.sales_tax_rate::NUMERIC/100::NUMERIC) * so.extended_price)::NUMERIC(16, 2) as total_cost_tax,
    (
         COALESCE(so.extended_price, 0)
        -COALESCE(nexternal_shipping.weighted_average_shipping, 0)
        -COALESCE((so.sales_tax_rate::NUMERIC/100::NUMERIC) * so.extended_price, 0)
    )::NUMERIC(16, 2) as total_margin,
    so.shipping_method,
    so.tracking_number,
    so.ship_to_state,
    so.unit_weight,
    so.total_weight,
    weight_bucket
FROM
    "public"."sales_orders_nexternal" so
    LEFT JOIN public.item_master_nexternal ON TRIM(so.product_sku) = TRIM(item_master_nexternal.sku)
    LEFT JOIN nexternal_shipping ON
        so.order_number = nexternal_shipping.order_number AND
        so.order_line = nexternal_shipping.order_line
    LEFT JOIN public.item_master_nexternal_no_sku no_sku ON 
        TRIM(so.product_name) = TRIM(no_sku.name) AND
        TRIM(COALESCE(so.product_attribute, '')) = TRIM(COALESCE(no_sku.attribute, ''))
    
UNION ALL

SELECT
    'Amazon'::TEXT as platform,
    so.order_status,
    so.amazon_order_id,
    NULL::INTEGER as order_line,
    so.purchase_date::DATE as order_date,
    DATE_PART('YEAR', so.purchase_date)::INTEGER as order_year,
    DATE_PART('MONTH', so.purchase_date)::INTEGER as order_month,
    NULL::DATE as ship_date,
    'Consumer'::TEXT as customer_type,
    n.marketing_category,
    n.supply_chain_category,
    so.product_name as product_name_historical,
    n.name as product_name_nexternal,
    (
        n.supply_chain_name || 
        CASE WHEN n.measure IS NOT NULL THEN ' ' || measure::NUMERIC(16, 1)::TEXT ELSE '' END ||
        CASE WHEN n.unit_of_measure IS NOT NULL THEN unit_of_measure ELSE '' END 
    ) as supply_chain_name,
    n.sku as nexternal_sku,
    so.asin as amazon_asin,
    NULL::TEXT as product_attribute,
    (so.item_price / CASE WHEN so.quantity = 0 THEN NULL ELSE so.quantity END)::NUMERIC(16, 2) as unit_sale_price,
    (so.shipping_price / CASE WHEN so.quantity = 0 THEN 1 ELSE so.quantity END)::NUMERIC(16, 2) as unit_cost_shipping,
    (so.item_tax / CASE WHEN so.quantity = 0 THEN 1 ELSE so.quantity END)::NUMERIC(16, 2) as unit_cost_shipping,
    (
        COALESCE((so.item_price / CASE WHEN so.quantity = 0 THEN NULL ELSE so.quantity END), 0)::NUMERIC(16, 2)
        -COALESCE((so.shipping_price / CASE WHEN so.quantity = 0 THEN 1 ELSE so.quantity END), 0)::NUMERIC(16, 2)
        -COALESCE((so.item_tax / CASE WHEN so.quantity = 0 THEN 1 ELSE so.quantity END), 0)::NUMERIC(16, 2)
    )::NUMERIC(16, 2) as unit_margin,
    so.quantity,
    so.item_price as total_sales,
    (COALESCE(so.shipping_price, 0) + COALESCE(so.shipping_tax, 0))::NUMERIC(16, 2) as total_cost_shipping,
    so.item_tax as total_cost_tax,
    (
         COALESCE(so.item_price, 0)
        -COALESCE(so.item_tax, 0)
        -COALESCE(so.shipping_price, 0)
    )::NUMERIC(16, 2) as total_margin,
    so.ship_service_level as shipping_method,
    NULL::TEXT as tracking_number,
    so.ship_state as ship_to_state,
    n.unit_weight,
    (n.unit_weight * so.quantity)::NUMERIC(16, 2) as total_weight,
    NULL::TEXT as weight_bucket
FROM
    "public"."sales_orders_amazon" so
    LEFT JOIN public.item_master_amazon a ON so.asin = a.asin
    LEFT JOIN public.item_master_nexternal n ON a.nexternal_sku = n.sku