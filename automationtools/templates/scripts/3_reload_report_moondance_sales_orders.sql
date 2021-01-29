CREATE TEMP TABLE adder_rates ON COMMIT DROP AS
    WITH rates AS (
        SELECT
            'Shopify Web' as sales_channel,
            'Shopify Order Prep Labor' as rate_name,
            'Labor' as rate_type,
            'Per Order' as rate_application,
            15.00 as hourly_rate,
            6::NUMERIC as minutes,
            NULL::NUMERIC as material_cost
    
        UNION ALL
        
        SELECT
            'Shopify Web' as sales_channel,
            'Shopify Order Line Fulfillment' as rate_name,
            'Labor' as rate_type,
            'Per Order Line' as rate_application,
            15.00 as hourly_rate,
            2::NUMERIC as minutes,
            NULL::NUMERIC as material_cost
    
        UNION ALL
    
        SELECT
            'Amazon FBM' as sales_channel,
            'FBM Order Prep Labor' as rate_name,
            'Labor' as rate_type,
            'Per Order' as rate_application,
            15.00 as hourly_rate,
            6::NUMERIC as minutes,
            NULL::NUMERIC as material_cost
    
        UNION ALL
        
        SELECT
            'Amazon FBM' as sales_channel,
            'FBM Order Line Fulfillment' as rate_name,
            'Labor' as rate_type,
            'Per Order Line' as rate_application,
            15.00 as hourly_rate,
            2::NUMERIC as minutes,
            NULL::NUMERIC as material_cost
    
        UNION ALL
        
        SELECT
            'Amazon FBM' as sales_channel,
            'FBM Order Packaging' as rate_name,
            'Materials' as rate_type,
            'Per Order' as rate_application,
            NULL::NUMERIC as hourly_rate,
            NULL::NUMERIC as minutes,
            0.75 as material_cost
    
        UNION ALL
        
        SELECT
            'Amazon FBA' as sales_channel,
            'FBA Order Line Prep' as rate_name,
            'Labor' as rate_type,
            'Per Order Line' as rate_application,
            15.00 as hourly_rate,
            6::NUMERIC as minutes,
            NULL::NUMERIC as material_cost
    )
        
    SELECT
        sales_channel,
        rate_application,
        ARRAY_AGG(rate_name::TEXT || ' - ' || minutes::TEXT || ' minutes at ' || hourly_rate || ' per hour') as rate_description,
        SUM((hourly_rate/60::NUMERIC) * minutes)::NUMERIC(16, 2) as labor_cost,
        SUM(material_cost) as material_cost
    FROM
        rates
    GROUP BY
        sales_channel,
        rate_application
    ;


CREATE TEMP TABLE sales_orders ON COMMIT DROP AS
WITH shopify_line_items AS (
    SELECT
        jsonb_array_elements(line_items) as line_json,
        CASE
            WHEN source_name = 'sell-on-amazon' THEN 'Amazon FBM'
            WHEN source_name IN ('580111', 'web', 'shopify_draft_order') or customer->>'tags' LIKE '%wholesaler%' THEN 'Shopify Web'
            WHEN source_name IN ('android', 'pos', 'iphone') THEN 'POS'
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
        tags,
        refunds,
        total_weight,
        (total_shipping_price_set->'shop_money'->>'amount')::NUMERIC(16, 2) as shipping_collected
    FROM
        shopify.shopify_sales_order
    WHERE
        financial_status NOT IN ('voided', 'refunded')
)
, shopify_refunds AS (
    WITH lines AS (
        SELECT
            (jsonb_array_elements((jsonb_array_elements(refunds)->'refund_line_items')))->'line_item'->>'id' as order_line_id,
            ((jsonb_array_elements((jsonb_array_elements(refunds)->'refund_line_items')))->>'quantity')::INTEGER as quantity
        FROM
            shopify.shopify_sales_order
    )
    
    SELECT
        order_line_id,
        SUM(quantity) as quantity
    FROM
        lines
    GROUP BY
        order_line_id
)
, shipping_paid AS (
    SELECT
        order_id,
        (regexp_matches(message, '[0-9]+\.?[0-9]*'))[1]::NUMERIC(16, 2) as amount
    FROM
        shopify.shopify_order_events
    WHERE
        verb = 'shipping_label_created_success'
)
, shipping_easy AS (
    SELECT
        so.id as order_id,
        SUM("Postage Cost") as shipping_fees
    FROM
        shopify.shipping_easy_orders easy JOIN
        shopify.shopify_sales_order so ON '#' || easy."Order Number" = so.name
    GROUP BY
        so.id    
)
, shopify_shipping_allocation AS (
    WITH shipping_line AS (
        SELECT 
            so.id as order_id,
            so.shipping_collected,
            so.line_json->>'id' as order_line_id,
            ((so.line_json->>'quantity')::INTEGER  - COALESCE(shopify_refunds.quantity, 0)) * CASE WHEN so.line_json->>'grams' = '0' THEN 1 ELSE (so.line_json->>'grams')::NUMERIC END as line_weight
        FROM
            shopify_line_items so LEFT JOIN
            shopify_refunds ON (so.line_json->>'id') = shopify_refunds.order_line_id LEFT JOIN
            public.operations_product p ON (so.line_json->>'product_id') = p.id::TEXT
    )
    , shipping_total AS (
        SELECT
            order_id,
            SUM(line_weight) as total_weight
        FROM
            shipping_line
        GROUP BY
            order_id
    )

    SELECT

        shipping_line.order_line_id,
        --line_weight / total_weight as allocated_weight,
        (shipping_line.shipping_collected * (line_weight / total_weight))::NUMERIC(16, 2) as shipping_collected,
        (
            COALESCE(shipping_paid.amount, shipping_easy.shipping_fees) * (line_weight / total_weight)
        )::NUMERIC(16, 2) as shipping_paid
    FROM
        shipping_total JOIN
        shipping_line ON shipping_total.order_id = shipping_line.order_id LEFT JOIN
        shipping_paid ON shipping_total.order_id = shipping_paid.order_id LEFT JOIN
        shipping_easy ON shipping_total.order_id = shipping_easy.order_id
)
, bundles AS (
    SELECT
        b.bundle_id,
        SUM(b.quantity::NUMERIC * top.unit_material_cost) as unit_material_cost
    FROM
        public.making_product_bundle_line b JOIN
        public.operations_product top ON b.product_used_id = top.id
    GROUP BY
        b.bundle_id
)
, amazon_fees AS (
    WITH lines AS (
        SELECT
            "FinancialEvents" as event,
            (jsonb_array_elements("ShipmentItemList")->>'OrderItemId')::BIGINT as "OrderItemId",
            -(jsonb_array_elements(jsonb_array_elements("ShipmentItemList")->'ItemFeeList')->'FeeAmount'->>'CurrencyAmount')::NUMERIC(16, 2) as fees
        FROM
            amazon.amazon_financial_events
    )

    SELECT
        "OrderItemId",
        SUM(fees) as total_fees
    FROM
        lines
    WHERE
        fees != 0
    GROUP BY
        "OrderItemId"    
)

SELECT
    CASE
        WHEN sales_channel = 'Amazon FBM' THEN 'Amazon'
        ELSE 'Shopify'
    END as source_system,
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
    ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))::INTEGER as quantity,
    (
        (line_json->>'price')::NUMERIC -
        COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
    )::NUMERIC(16, 2) as unit_sales_price,
    COALESCE(bundles.unit_material_cost, p.unit_material_cost) as unit_material_cost,   
    NULL::NUMERIC(16, 2) as unit_fulfillment_cost,
    COALESCE(bundles.unit_material_cost, p.unit_material_cost) as unit_cost, 
    (
        (
            (line_json->>'price')::NUMERIC -
            COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
        ) * ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))
    )::NUMERIC(16, 2) as total_sales,
    shopify_shipping_allocation.shipping_collected as total_shipping_collected,
    shopify_shipping_allocation.shipping_paid as total_shipping_paid,
    (
        COALESCE(shopify_shipping_allocation.shipping_collected, 0) -
        COALESCE(shopify_shipping_allocation.shipping_paid, 0)
    ) as total_shipping_margin,
    (
        COALESCE(bundles.unit_material_cost, p.unit_material_cost) *
        ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))
    )::NUMERIC(16, 2) as total_material_cost,
    NULL::NUMERIC(16, 2) as total_fulfillment_cost,
    (
        COALESCE(bundles.unit_material_cost, p.unit_material_cost) *
        ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))
    )::NUMERIC(16, 2) as total_cost,
    (
        (
            (line_json->>'price')::NUMERIC -
            COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
        ) - 
        (
            COALESCE(bundles.unit_material_cost, p.unit_material_cost, 0)
        )
    ) * ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0)) as total_margin,
    discount_applications->0->>'title' as discount_promotion_name,
    (line_json->'discount_allocations'->0->>'amount')::NUMERIC(16, 2) as total_discounts_given,
    CASE
        WHEN customer->>'tags' LIKE '%wholesaler%' THEN 'Wholesale'
        ELSE 'Retail'
    END  as customer_type,
    COALESCE((customer->>'first_name') || ' ' || (customer->>'last_name'), 'Unknown') as customer_name,
    customer->'default_address'->>'company' as company,
    CASE
        WHEN sales_channel = 'POS' AND shipping_address->>'province' IS NULL THEN 'North Carolina'
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
    shopify_line_items so LEFT JOIN
    public.integration_shopify_product sp ON (so.line_json->>'variant_id') = sp.variant_id::TEXT LEFT JOIN
    public.integration_product_missing_sku missing ON
        line_json->>'name' = missing.product_description AND
        missing.source_system = 'Shopify' AND
        sp.id IS NULL LEFT JOIN
    public.operations_product p ON COALESCE(sp.product_id, missing.product_id) = p.id LEFT JOIN
    public.operations_product_code pcode ON p.product_code_id = pcode.id LEFT JOIN
    bundles ON p.id = bundles.bundle_id LEFT JOIN
    shopify_refunds refunds ON (line_json->>'id') = refunds.order_line_id LEFT JOIN
    shopify_shipping_allocation ON (line_json->>'id') = shopify_shipping_allocation.order_line_id
    
UNION ALL

SELECT
    'Amazon' as source_system,
    CASE
        WHEN "FulfillmentChannel" = 'AFN' THEN 'Amazon FBA'
        WHEN "FulfillmentChannel" = 'MFN' THEN 'Amazon FBM'
    END as sales_channel,
    sl."AmazonOrderId" as order_id,
    sl."OrderItemId"::BIGINT as order_line_id,
    CASE
        WHEN "OrderStatus" IN ('Pending', 'Unshipped') THEN 'Pending'
        WHEN "OrderStatus" IN ('Shipped') THEN 'Shipped'
    END as order_status,
    CASE
        WHEN COALESCE(sl."QuantityOrdered", 0) - COALESCE(sl."QuantityShipped", 0) > 0 THEN 'Unfulfilled'
        ELSE 'Fulfilled'
    END as fulfillment_status,
    sl."AmazonOrderId" as order_number,
    pcode.family as product_family,
    pcode.category as product_category,
    product.sku as product_sku,
    product.description as product_description,
    sl."ASIN" as source_product_id,
    sl."SellerSKU" as source_product_sku,
    sl."Title" as source_product_name,
    sl."QuantityOrdered" as quantity,
    ((sl."ItemPrice"->>'Amount')::NUMERIC(16, 2) / sl."QuantityOrdered")::NUMERIC(16, 2) as unit_sales_price,
    COALESCE(bundles.unit_material_cost, product.unit_material_cost)::NUMERIC(16, 2) as unit_material_cost,
    (amazon_fees.total_fees / sl."QuantityOrdered")::NUMERIC(16, 2) as unit_fulfillment_cost,
    (
        COALESCE(bundles.unit_material_cost, product.unit_material_cost, 0) +
        COALESCE((amazon_fees.total_fees / sl."QuantityOrdered")::NUMERIC(16, 2), 0)
    )::NUMERIC(16, 2) as unit_cost,
    (sl."ItemPrice"->>'Amount')::NUMERIC(16, 2) as total_sales,
    NULL::NUMERIC(16, 2) as total_shipping_collected,
    NULL::NUMERIC(16, 2) as total_shipping_paid,
    NULL::NUMERIC(16, 2) as total_shipping_margin,
    (COALESCE(bundles.unit_material_cost, product.unit_material_cost) * sl."QuantityOrdered")::NUMERIC(16, 2) as total_material_cost,
    amazon_fees.total_fees::NUMERIC(16, 2) as total_fulfillment_cost,
    (
        (COALESCE(bundles.unit_material_cost, product.unit_material_cost) * sl."QuantityOrdered") +
        COALESCE(amazon_fees.total_fees, 0)
    )::NUMERIC(16, 2) as total_cost,
    (
        (sl."ItemPrice"->>'Amount')::NUMERIC(16, 2) -
        (
            (COALESCE(bundles.unit_material_cost, product.unit_material_cost) * sl."QuantityOrdered") + COALESCE(amazon_fees.total_fees, 0)
        )
    )::NUMERIC(16, 2) as total_margin,
    NULL::TEXT as discount_promotion_name,
    ((sl."PromotionDiscount"->>'Amount')::NUMERIC(16, 2) / sl."QuantityOrdered")::NUMERIC(16, 2) as total_discounts_given,
    'Retail' as customer_type,
    NULL::TEXT as customer_name,
    NULL::TEXT as company,
    NULL::TEXT as ship_to_state,
    FALSE is_tax_exempt,
    sh._created as date_created,
    sh."LastUpdateDate" as date_last_updated,
    sh."PurchaseDate" as processed_date,
    DATE_PART('YEAR', sh."PurchaseDate")::INTEGER as processed_year,
    DATE_PART('MONTH', sh."PurchaseDate")::INTEGER as processed_month,
    DATE_TRUNC('MONTH', sh."PurchaseDate")::DATE as processed_period
FROM
    amazon.amazon_sales_order sh JOIN
    amazon.amazon_sales_order_line sl ON sh."AmazonOrderId" = sl."AmazonOrderId" LEFT JOIN
    public.integration_amazon_product ap ON sl."SellerSKU" = ap.seller_sku LEFT JOIN
    public.operations_product product ON ap.product_id = product.id LEFT JOIN
    public.operations_product_code pcode ON product.product_code_id = pcode.id LEFT JOIN
    bundles ON product.id = bundles.bundle_id  LEFT JOIN
    shopify.shopify_sales_order shopify ON sh."AmazonOrderId" = shopify.reference LEFT JOIN
    amazon_fees ON sl."OrderItemId" = amazon_fees."OrderItemId"
WHERE
    sh."OrderStatus" <> 'Canceled' AND
    shopify.id IS NULL -- don't double count between shopify and amazon
;


CREATE TEMP TABLE order_adder ON COMMIT DROP AS
    WITH order_lines AS (
        SELECT
            order_id,
            sales_channel,
            count(*) as order_line_count
        FROM
            sales_orders
        GROUP BY
            order_id,
            sales_channel
    )
    
    SELECT
        order_lines.order_id,
        order_lines.sales_channel,
        SUM((COALESCE(labor_cost, 0) + COALESCE(material_cost, 0)) / order_line_count) as cost_per_order
    FROM
        order_lines JOIN
        adder_rates ON 
            order_lines.sales_channel = adder_rates.sales_channel AND
            adder_rates.rate_application = 'Per Order'
    GROUP BY
        order_lines.order_id,
        order_lines.sales_channel
;


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
    quantity,
    unit_sales_price,
    unit_material_cost,
    unit_fulfillment_cost,
    unit_cost,
    total_sales,
    total_shipping_collected,
    total_shipping_paid,
    total_shipping_margin,
    total_material_cost,
    total_fulfillment_cost,
    total_cost,
    total_margin,
    discount_promotion_name,
    total_discounts_given,
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

SELECT
    so.source_system,
    so.sales_channel,
    so.order_id,
    so.order_line_id,
    so.order_status,
    so.fulfillment_status,
    so.order_number,
    so.product_family,
    so.product_category,
    so.product_sku,
    so.product_description,
    so.source_product_id,
    so.source_product_sku,
    so.source_product_name,
    so.quantity,
    so.unit_sales_price,
    so.unit_material_cost,
    (
        COALESCE(unit_fulfillment_cost, 0) + 
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
        
    ) as unit_fulfillment_cost,
    (
        COALESCE(unit_cost, 0) + 
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
    ) as unit_cost,
    total_sales,
    total_shipping_collected,
    total_shipping_paid,
    total_shipping_margin,
    total_material_cost,
    (
        COALESCE(total_fulfillment_cost, 0) +
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
    ) as total_fulfillment_cost,
    (
        COALESCE(total_cost, 0) +
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
    ) as total_cost,
    (
        COALESCE(total_margin, 0) -
        COALESCE(adder_line.labor_cost, 0) -
        COALESCE(adder_line.material_cost, 0) -
        COALESCE(order_adder.cost_per_order, 0)
    ) as total_margin,
    discount_promotion_name,
    total_discounts_given,
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
FROM
    sales_orders so LEFT JOIN
    adder_rates adder_line ON
        so.sales_channel = adder_line.sales_channel AND
        adder_line.rate_application = 'Per Order Line' LEFT JOIN
    order_adder ON
        so.sales_channel = order_adder.sales_channel AND
        so.order_id = order_adder.order_id
;

 