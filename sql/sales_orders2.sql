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
    COALESCE(item_master_nexternal.supply_chain_name, no_sku.supply_chain_name) as supply_chain_name,
    so.product_sku as nexternal_sku,
    NULL::TEXT as amazon_asin,
    so.product_attribute,
    so.extended_price as total_sales,
    so.quantity,
    so.unit_price as unit_sale_price,
    so.tracking_number,
    so.ship_to_state,
    so.unit_weight,
    so.total_weight
FROM
    "public"."sales_orders_nexternal" so
    LEFT JOIN public.item_master_nexternal ON TRIM(so.product_sku) = TRIM(item_master_nexternal.sku)
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
    n.supply_chain_name,
    n.sku as nexternal_sku,
    so.asin as amazon_asin,
    NULL::TEXT as product_attribute,
    so.item_price as total_sales,
    so.quantity,
    (so.item_price / CASE WHEN so.quantity = 0 THEN NULL ELSE so.quantity END)::NUMERIC(16, 2) as unit_sale_price,
    NULL::TEXT as tracking_number,
    so.ship_state as ship_to_state,
    n.unit_weight,
    (n.unit_weight * so.quantity)::NUMERIC(16, 2) as total_weight
FROM
    "public"."sales_orders_amazon" so
    LEFT JOIN public.item_master_amazon a ON so.asin = a.asin
    LEFT JOIN public.item_master_nexternal n ON a.nexternal_sku = n.sku