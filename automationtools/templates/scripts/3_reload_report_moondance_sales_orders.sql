TRUNCATE TABLE report_moondance.sales_orders;

INSERT INTO report_moondance.sales_orders (
    source_system,
    sales_channel,
    order_id,
    order_line_id,
    order_status,
    fulfillment_status,
    order_number,
    product_family,
    product_category,
    product_sku,
    product_description,
    source_product_id,
    source_product_sku,
    source_product_name,
    unit_sales_price,
    unit_cost,
    total_sales,
    total_cost,
    total_margin,
    discount_promotion_name,
    total_discounts_given,
    quantity,
    customer_type,
    customer_name,
    company,
    ship_to_state,
    is_tax_exempt,
    date_created,
    date_last_updated,
    processed_date,
    processed_year,
    processed_month,
    processed_period
)

WITH line_items AS (
    SELECT
        jsonb_array_elements(line_items) as line_json,
        CASE
            WHEN source_name = 'sell-on-amazon' THEN 'Amazon FBM'
            WHEN source_name IN ('580111', 'web', 'shopify_draft_order') or customer->>'tags' LIKE '%wholesaler%' THEN 'Shopify Web'
            WHEN source_name IN ('android', 'pos', 'iphone') THEN 'Farmer''s Market'
            ELSE source_name
        END as sales_channel,
        customer,
        shipping_address,
        id,
        closed_at,
        created_at,
        updated_at,
        number,
        note,
        financial_status,
        total_discounts,
        total_line_items_price,
        name,
        processed_at,
        order_number,
        discount_applications,
        fulfillment_status,
        tags
    FROM
        public.shopify_sales_order
)

SELECT
    'Shopify' as source_system,
    sales_channel,
    so.id::TEXT as order_id,
    (line_json->>'id')::BIGINT as order_line_id,
    CASE
        WHEN financial_status IN ('pending') THEN 'Pending'
        WHEN fulfillment_status IN ('fulfilled') THEN 'Shipped'
        ELSE 'Pending'
    END as order_status,
    INITCAP(COALESCE((line_json->>'fulfillment_status'), 'unfulfilled')) as fulfillment_status,  
    name as order_number,
    pcode.family as product_family,
    pcode.category as product_category,
    p.sku as product_sku,
    p.description as product_description,
    (line_json->>'variant_id') as source_product_id,
    COALESCE(sp.shopify_sku::TEXT, (line_json->>'sku')) as source_product_sku,
    line_json->>'name' as source_product_name,
    (
        (line_json->>'price')::NUMERIC -
        COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
    )::NUMERIC(16, 2) as unit_sales_price,
        p.unit_material_cost as unit_cost,
    (
        (
            (line_json->>'price')::NUMERIC -
            COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
        ) * (line_json->>'quantity')::NUMERIC
    )::NUMERIC(16, 2) as total_sales,
    (p.unit_material_cost * (line_json->>'quantity')::NUMERIC)::NUMERIC(16, 2) as total_cost,
    (
        (
            (line_json->>'price')::NUMERIC -
            COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
        ) * (line_json->>'quantity')::NUMERIC
    )::NUMERIC(16, 2) - COALESCE((p.unit_material_cost * (line_json->>'quantity')::NUMERIC), 0)::NUMERIC(16, 2) as total_margin,
    
    discount_applications->0->>'title' as discount_promotion_name,
    COALESCE(line_json->'discount_allocations'->0->>'amount') as total_discounts_given,
    (line_json->>'quantity')::INTEGER as quantity,
    CASE
        WHEN customer->>'tags' LIKE '%wholesaler%' THEN 'Wholesale'
        ELSE 'Retail'
    END  as customer_type,
    COALESCE((customer->>'first_name') || ' ' || (customer->>'last_name'), 'Unknown') as customer_name,
    customer->'default_address'->>'company' as company,
    CASE
        WHEN sales_channel = 'Farmer''s Market' AND shipping_address->>'province' IS NULL THEN 'North Carolina'
        WHEN shipping_address->>'province' IS NULL THEN 'North Carolina' -- pickup
        WHEN shipping_address->>'province' = 'NC' THEN 'North Carolina'
        ELSE shipping_address->>'province'
    END as ship_to_state,
    COALESCE((customer->>'tax_exempt')::BOOLEAN, FALSE) as is_tax_exempt,
    created_at::TIMESTAMP WITH TIME ZONE as date_created,
    updated_at::TIMESTAMP WITH TIME ZONE as date_last_updated,
    processed_at::TIMESTAMP WITH TIME ZONE as processed_date,
    DATE_PART('YEAR', processed_at::TIMESTAMP WITH TIME ZONE)::INTEGER as processed_year,
    DATE_PART('MONTH', processed_at::TIMESTAMP WITH TIME ZONE)::INTEGER as processed_month,
    DATE_TRUNC('MONTH', processed_at::TIMESTAMP WITH TIME ZONE)::DATE as processed_period
FROM
    line_items so LEFT JOIN
    public.operations_shopify_product sp ON (so.line_json->>'variant_id') = sp.variant_id::TEXT LEFT JOIN
    public.operations_product_missing_sku missing ON
        line_json->>'name' = missing.product_description AND
        missing.source_system = 'Shopify' AND
        sp.id IS NULL LEFT JOIN
    public.operations_product p ON COALESCE(sp.product_id, missing.product_id) = p.id LEFT JOIN
    public.operations_product_code pcode ON p.product_code_id = pcode.id
WHERE
    financial_status NOT IN ('voided', 'refunded') AND
    CASE
        WHEN line_json->>'fulfillment_status' IS NULL AND financial_status = 'partially_refunded' THEN 0
        ELSE 1
    END = 1
    --AND (line_json->>'sku') = 'SE-XFRST'
;