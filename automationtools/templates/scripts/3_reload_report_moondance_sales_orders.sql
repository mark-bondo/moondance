/*
TODO
    add order level discounts
*/

CREATE TEMP TABLE default_costs ON COMMIT DROP AS
    SELECT 0.20::NUMERIC as percent, 'materials' as type
    UNION ALL
    SELECT 0.10::NUMERIC as percent, 'labor' as type
;


CREATE TEMP TABLE order_line_taxes ON COMMIT DROP AS
    WITH tax_detail AS (
        SELECT
            jsonb_array_elements(line_items)->>'id' as order_line_id,
            jsonb_array_elements(jsonb_array_elements(line_items)->'tax_lines')->>'title' as tax_types,
            (jsonb_array_elements(jsonb_array_elements(line_items)->'tax_lines')->>'price')::NUMERIC as taxes_collected
        FROM
            shopify.shopify_sales_order
    )

    SELECT
        order_line_id::BIGINT as order_line_id,
        SUM(taxes_collected) as taxes_collected,
        (ARRAY_REMOVE(ARRAY_AGG(DISTINCT tax_types ORDER BY tax_types), 'North Carolina State Tax'))[1] as county
    FROM
        tax_detail
    GROUP BY
        order_line_id::BIGINT
;


CREATE TEMP TABLE sales_orders ON COMMIT DROP AS
WITH shopify_line_items AS (
    SELECT
        jsonb_array_elements(so.line_items) as line_json,
        CASE
            WHEN so.source_name = 'sell-on-amazon' THEN 'Amazon FBM'
            WHEN COALESCE(c.tags, so.customer->>'tags') ILIKE '%wholesale%' OR so.tags ILIKE '%wholesale%' THEN 'Wholesale'
            WHEN so.location_id::BIGINT = 61831086229 THEN 'Farmers Market - Wake Forest'
            WHEN 
                (so.source_name IN ('android', 'pos', 'iphone') AND EXTRACT('DOW' FROM so.processed_at::DATE) = 6) 
                OR 
                so.location_id::BIGINT = 61830463637 
                THEN 'Farmers Market - Durham'
            WHEN so.source_name IN ('279941', '580111', 'web', 'shopify_draft_order', 'android', 'pos', 'iphone') THEN 'Shopify Retail'
            ELSE so.source_name
        END as sales_channel,
        COALESCE((customer->>'first_name') || ' ' || (customer->>'last_name'), 'Unknown') as customer_name,
        COALESCE(
            NULLIF(customer->'default_address'->>'company', ''), 
            CASE 
                WHEN COALESCE(c.tags, so.customer->>'tags') ILIKE '%wholesale%' OR so.tags ILIKE '%wholesale%' THEN COALESCE((customer->>'first_name') || ' ' || (customer->>'last_name'), 'Unknown') 
            END
        ) as company,
        CASE
            WHEN COALESCE(c.tags, so.customer->>'tags') ILIKE '%wholesale%' OR so.tags ILIKE '%wholesale%' THEN 'Wholesale'
            ELSE 'Retail'
        END as customer_type,
        so.shipping_address,
        so.id,
        so.closed_at,
        so.created_at,
        so.updated_at,
        so.created_at as date_created,
        so.updated_at as date_last_updated,
        so.processed_at as processed_date,
        DATE_PART('YEAR', so.processed_at)::INTEGER as processed_year,
        DATE_PART('MONTH', so.processed_at)::INTEGER as processed_month,
        DATE_TRUNC('MONTH', so.processed_at)::DATE as processed_period,
        so.number,
        so.note,
        CASE
            WHEN financial_status IN ('pending') THEN 'Pending'
            WHEN fulfillment_status IN ('fulfilled') THEN 'Shipped'
            ELSE 'Pending'
        END as order_status,
        COALESCE((customer->>'tax_exempt')::BOOLEAN, FALSE) as is_tax_exempt,
        so.total_discounts,
        so.name as order_number,
        so.discount_applications->0->>'title' as discount_promotion_name,
        so.refunds,
        so.total_weight,
        so.reference,
        (so.total_shipping_price_set->'shop_money'->>'amount')::NUMERIC(16, 2) as shipping_collected
    FROM
        shopify.shopify_sales_order so
        LEFT JOIN shopify.shopify_customer c ON (so.customer->>'id')::BIGINT = c.id 
    WHERE
        so.financial_status NOT IN ('voided', 'refunded')
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
, shipping_tax_collected AS (
    WITH lines AS (
        SELECT
            id as order_id,
            ((jsonb_array_elements((jsonb_array_elements(shipping_lines)->'tax_lines')))->>'price')::NUMERIC as tax_collected
        FROM
            shopify.shopify_sales_order
    )
    
    SELECT
        order_id,
        SUM(tax_collected) as tax_collected
    FROM
        lines
    GROUP BY
        order_id
)
, shipping_paid AS (
    SELECT
        DISTINCT ON (order_id)
        order_id,
        (regexp_matches(message, '[0-9]+\.?[0-9]*'))[1]::NUMERIC(16, 2) as amount
    FROM
        shopify.shopify_order_events
    WHERE
        verb = 'shipping_label_created_success'
    ORDER BY
        order_id,
        created_at DESC
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
        (shipping_line.shipping_collected * (line_weight / total_weight)) as shipping_collected,
        (tax.tax_collected * (line_weight / total_weight)) as shipping_tax_collected,
        (
            COALESCE(shipping_paid.amount, shipping_easy.shipping_fees) * (line_weight / total_weight)
        ) as shipping_cost
    FROM
        shipping_total JOIN
        shipping_line ON shipping_total.order_id = shipping_line.order_id LEFT JOIN
        shipping_paid ON shipping_total.order_id = shipping_paid.order_id LEFT JOIN
        shipping_easy ON shipping_total.order_id = shipping_easy.order_id LEFT JOIN
        shipping_tax_collected tax ON 
            shipping_total.order_id = tax.order_id AND
            tax.tax_collected <> 0
)
, amazon_fees AS (
    WITH events AS (
        SELECT
            "FinancialEvents" as event,
            "AmazonOrderId",
            (jsonb_array_elements("ShipmentItemList")->>'OrderItemId')::BIGINT as "OrderItemId",
            -(jsonb_array_elements(jsonb_array_elements("ShipmentItemList")->'ItemFeeList')->'FeeAmount'->>'CurrencyAmount')::NUMERIC(16, 2) as fees
        FROM
            amazon.amazon_financial_events
    )

    SELECT
        events."AmazonOrderId",
        events."OrderItemId",
        i.product_id,
        SUM(fees) as total_fees
    FROM
        events
        JOIN amazon.amazon_sales_order_line line ON events."OrderItemId" = line."OrderItemId"
        JOIN public.integration_amazon_product i ON line."ASIN" = i.asin
    WHERE
        fees != 0
    GROUP BY
        events."AmazonOrderId",
        events."OrderItemId",
        i.product_id

)

SELECT
    CASE
        WHEN so.sales_channel = 'Amazon FBM' THEN 'Amazon'
        ELSE 'Shopify'
    END as source_system,
    so.sales_channel,
    so.id::TEXT as order_id,
    (line_json->>'id')::BIGINT as order_line_id,
    so.order_status,
    INITCAP(COALESCE((line_json->>'fulfillment_status'), 'unfulfilled')) as fulfillment_status,
    so.order_number,
    pcode.family as product_family,
    pcode.category as product_category,
    COALESCE(p.sku, psku.sku) as product_sku,
    COALESCE(p.description, psku.description, line_json->>'name') as product_description,
    (line_json->>'variant_id') as source_product_id,
    COALESCE(sp.shopify_sku::TEXT, (line_json->>'sku')) as source_product_sku,
    line_json->>'name' as source_product_name,
    CASE
        WHEN ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))::INTEGER = 0 THEN NULL
        ELSE ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))::INTEGER
    END as quantity,
    (
        (
            (line_json->>'price')::NUMERIC -
            COALESCE(((line_json->'discount_allocations'->0->>'amount')::NUMERIC/(line_json->>'quantity')::NUMERIC), 0)
        ) * ((line_json->>'quantity')::NUMERIC - COALESCE(refunds.quantity, 0))
    ) as net_sales,
    shopify_shipping_allocation.shipping_collected,
    shopify_shipping_allocation.shipping_tax_collected,
    shopify_shipping_allocation.shipping_cost as shipping_cost,
   (
        COALESCE(
            p.unit_material_cost + COALESCE(p.unit_freight_cost, 0),
            (SELECT percent FROM default_costs WHERE type = 'materials') * (line_json->>'price')::NUMERIC
        ) *
        (
            (line_json->>'quantity')::NUMERIC - 
            COALESCE(refunds.quantity, 0)
        )
    ) as material_cost,
    (
        COALESCE(
            p.unit_labor_cost,
            (SELECT percent FROM default_costs WHERE type = 'labor') * (line_json->>'price')::NUMERIC
        ) *
        (
            (line_json->>'quantity')::NUMERIC -
            COALESCE(refunds.quantity, 0)
        )
    ) as direct_labor,
    amazon_fees.total_fees as sales_channel_fees,
    so.discount_promotion_name,
    (line_json->'discount_allocations'->0->>'amount')::NUMERIC as total_discounts_given,
    so.customer_type,
    so.customer_name,
    so.company,
    CASE
        WHEN sales_channel LIKE 'Farmers Market%' AND shipping_address->>'province' IS NULL THEN 'North Carolina'
        WHEN shipping_address->>'province' IS NULL THEN 'North Carolina' -- pickup
        WHEN shipping_address->>'province' = 'NC' THEN 'North Carolina'
        ELSE shipping_address->>'province'
    END as ship_to_state,
    so.is_tax_exempt,
    so.date_created,
    so.date_last_updated,
    so.processed_date,
    so.processed_year,
    so.processed_month,
    so.processed_period,
    CASE
        WHEN p.unit_material_cost IS NULL THEN 'Product Cost'
        ELSE 'Average Cost'
    END as cost_type
FROM
    shopify_line_items so 
    LEFT JOIN public.integration_shopify_product sp ON (so.line_json->>'variant_id') = sp.variant_id::TEXT 
    LEFT JOIN public.integration_product_missing_sku missing ON
        line_json->>'name' = missing.product_description AND
        missing.source_system = 'Shopify' AND
        sp.id IS NULL 
    LEFT JOIN public.operations_product psku ON so.line_json->>'sku' = psku.sku 
    LEFT JOIN public.operations_product p ON COALESCE(sp.product_id, missing.product_id) = p.id 
    LEFT JOIN public.operations_product_code pcode ON COALESCE(p.product_code_id, psku.product_code_id) = pcode.id 
    LEFT JOIN shopify_refunds refunds ON (line_json->>'id') = refunds.order_line_id 
    LEFT JOIN shopify_shipping_allocation ON (line_json->>'id') = shopify_shipping_allocation.order_line_id 
    LEFT JOIN amazon_fees ON 
        so.reference = amazon_fees."AmazonOrderId" AND
        p.id = amazon_fees.product_id
        
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
    CASE 
		WHEN sl."QuantityOrdered" = 0 THEN NULL 
		ELSE sl."QuantityOrdered" 
	END as quantity,
    (sl."ItemPrice"->>'Amount')::NUMERIC as net_sales,
    NULL::NUMERIC as shipping_collected,
    NULL::NUMERIC as shipping_tax_collected,
    NULL::NUMERIC as shipping_cost,
    (
        COALESCE(
            (product.unit_material_cost + COALESCE(product.unit_freight_cost, 0)) * sl."QuantityOrdered",
            (SELECT percent FROM default_costs WHERE type = 'materials') * (sl."ItemPrice"->>'Amount')::NUMERIC
        )
    )::NUMERIC as material_cost,
    (
        COALESCE(
            (product.unit_labor_cost) * sl."QuantityOrdered",
            (SELECT percent FROM default_costs WHERE type = 'labor') * (sl."ItemPrice"->>'Amount')::NUMERIC
        )
    )::NUMERIC as direct_labor,
    amazon_fees.total_fees::NUMERIC as sales_channel_fees,
    NULL::TEXT as discount_promotion_name,
    ((sl."PromotionDiscount"->>'Amount')::NUMERIC(16, 2) / sl."QuantityOrdered")::NUMERIC as total_discounts_given,
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
    DATE_TRUNC('MONTH', sh."PurchaseDate")::DATE as processed_period,
    CASE
        WHEN product.unit_material_cost IS NULL THEN 'Product Cost'
        ELSE 'Average Cost'
    END as cost_type
FROM
    amazon.amazon_sales_order sh JOIN
    amazon.amazon_sales_order_line sl ON sh."AmazonOrderId" = sl."AmazonOrderId" LEFT JOIN
    public.integration_amazon_product ap ON sl."ASIN" = ap.asin LEFT JOIN
    public.operations_product product ON ap.product_id = product.id LEFT JOIN
    public.operations_product_code pcode ON product.product_code_id = pcode.id LEFT JOIN
    shopify.shopify_sales_order shopify ON sh."AmazonOrderId" = shopify.reference LEFT JOIN
    amazon_fees ON sl."OrderItemId" = amazon_fees."OrderItemId"
WHERE
    sh."OrderStatus" <> 'Canceled' AND
    shopify.id IS NULL -- don't double count between shopify and amazon

UNION ALL

SELECT
    'Nexternal' as source_system,
    CASE
        WHEN customer_type = 'Business' THEN 'Wholesale' 
        ELSE 'Nexternal Retail'
    END as sales_channel,
    order_number::TEXT as order_id,
    order_line as order_line_id,
    order_line_status,
    order_line_status as fulfillment_status,
    order_number::TEXT as order_number,
    pcode.family as product_family,
    pcode.category as product_category,
    product_sku as product_sku,
    COALESCE(item.description, product_name) as product_description,
    product_sku as source_product_id,
    product_sku as source_product_sku,
    product_name as source_product_name,
    quantity,
    extended_price as net_sales,
    shipping_rate as shipping_collected,
    NULL::NUMERIC as shipping_tax_collected,
    NULL::NUMERIC as shipping_cost,
    NULL::NUMERIC as material_cost,
    NULL::NUMERIC as direct_labor,
    NULL::NUMERIC as sales_channel_fees,
    NULL::TEXT as discount_promotion_name,
    NULL::NUMERIC as total_discounts_given,
    CASE
        WHEN customer_type = 'Business' THEN 'Wholesale' 
        ELSE 'Retail'
    END as customer_type,
    NULL::TEXT as customer_name,
    NULL::TEXT as company,
    ship_to_state,
    CASE
        WHEN sales_tax_rate = 0 THEN TRUE
        ELSE FALSE
    END as is_tax_exempt,
    so._created as date_created,
    so._updated as date_last_updated,
    datetime_ordered::DATE as processed_date,
    DATE_PART('YEAR', datetime_ordered)::INTEGER as processed_year,
    DATE_PART('MONTH', datetime_ordered)::INTEGER as processed_month,
    DATE_TRUNC('MONTH', datetime_ordered)::DATE as processed_period,
    CASE
        WHEN item.unit_material_cost IS NULL THEN 'Product Cost'
        ELSE 'Average Cost'
    END as cost_type
FROM
    nexternal.sales_order so
    LEFT JOIN public.operations_product item ON so.product_sku = item.sku
    LEFT JOIN public.operations_product_code pcode ON item.product_code_id = pcode.id
WHERE
    datetime_ordered >= '2019-01-01' AND
    order_status != 'Canceled' AND
    COALESCE(product_name, '') NOT LIKE '% Insert'

UNION ALL

SELECT
    'Excel' as source_system,
    'Farmers Market - Durham' as sales_channel,
    NULL::TEXT as order_id,
    NULL::INTEGER as order_line_id,
    NULL::TEXT as order_line_status,
    NULL::TEXT as fulfillment_status,
    NULL::TEXT as order_number,
    NULL::TEXT as product_family,
    NULL::TEXT as product_category,
    NULL::TEXT as product_sku,
    NULL::TEXT as product_description,
    NULL::TEXT as source_product_id,
    NULL::TEXT as source_product_sku,
    NULL::TEXT as source_product_name,
    NULL::NUMERIC as quantity,
    total_sales as net_sales,
    NULL::NUMERIC as shipping_collected,
    NULL::NUMERIC as shipping_tax_collected,
    NULL::NUMERIC as shipping_cost,
    NULL::NUMERIC as material_cost,
    NULL::NUMERIC as direct_labor,
    NULL::NUMERIC as sales_channel_fees,
    NULL::TEXT as discount_promotion_name,
    NULL::NUMERIC as total_discounts_given,
    'Retail' as customer_type,
    NULL::TEXT as customer_name,
    NULL::TEXT as company,
    'North Carolina' as ship_to_state,
    FALSE as is_tax_exempt,
    _created as date_created,
    _created as date_last_updated,
    date_shipped as processed_date,
    DATE_PART('YEAR', date_shipped)::INTEGER as processed_year,
    DATE_PART('MONTH', date_shipped)::INTEGER as processed_month,
    DATE_TRUNC('MONTH', date_shipped)::DATE as processed_period,
    'Average Cost' as cost_type
FROM
    public.accounting_farmers_market_sales_history
;

CREATE TEMP TABLE order_count ON COMMIT DROP AS
    SELECT
        order_id,
        sales_channel,
        count(*) as order_line_count,
        sum(COALESCE(net_sales, 0) + COALESCE(shipping_collected, 0)) as total_sales
    FROM
        sales_orders
    GROUP BY
        order_id,
        sales_channel

;

CREATE TEMP TABLE adder_rates ON COMMIT DROP AS
    SELECT
        type,
        sales_channel,
        apply_to,
        ARRAY_AGG(name::TEXT || ' - ' || labor_minutes::TEXT || ' minutes at ' || labor_hourly_rate || ' per hour') as overlay_description,
        SUM((labor_hourly_rate::NUMERIC/60::NUMERIC) * labor_minutes::NUMERIC) as labor_cost,
        SUM(material_cost) as material_cost,
        SUM(sales_percentage / 100::NUMERIC) as sales_percentage_fee
    FROM
        public.operations_order_cost_overlay
    GROUP BY
        type,
        sales_channel,
        apply_to
;


CREATE TEMP TABLE order_adder ON COMMIT DROP AS
    SELECT
        order_count.order_id,
        order_count.sales_channel,
        SUM(
            (
                CASE 
                    WHEN type IN ('Fulfillment Labor', 'Shipping Materials') THEN
                        COALESCE(labor_cost, 0) + 
                        COALESCE(material_cost, 0) +
                        COALESCE(sales_percentage_fee * total_sales, 0)
                END
            ) / order_line_count
        ) as adder_fullfilment_cost,
        SUM(
            (
                CASE 
                    WHEN type IN ('Sales Channel Fees') THEN
                        COALESCE(labor_cost, 0) + 
                        COALESCE(material_cost, 0) +
                        COALESCE(sales_percentage_fee * total_sales, 0)
                END
            ) / order_line_count
        ) as adder_sales_channel_fees
    FROM
        order_count JOIN
        adder_rates ON 
            order_count.sales_channel = adder_rates.sales_channel AND
            adder_rates.apply_to = 'Each Order'
    GROUP BY
        order_count.order_id,
        order_count.sales_channel
;


TRUNCATE TABLE report_moondance.sales_orders;
INSERT INTO report_moondance.sales_orders (
    source_system,
    sales_channel_type,
    sales_channel_name,
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
    unit_direct_labor,
    unit_moondance_fulfillment_cost,
    unit_sales_channel_fees,
    unit_cost,
    net_sales,
    shipping_collected,
    shipping_cost,
    shipping_margin,
    material_cost,
    direct_labor,
    moondance_fulfillment_cost,
    sales_channel_fees,
    total_cost,
    product_margin,
    gross_profit,
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
    processed_period,
    cost_type,
    order_count,
    county_tax_name,
    state_tax_name,
    county_transit_tax_rate,
    county_base_tax_rate,
    state_tax_rate,
    total_county_transit_tax,
    total_county_base_tax,
    total_state_tax,
    taxes_collected,
    total_gross_sales
)

SELECT
    so.source_system,
    CASE
        WHEN so.sales_channel ILIKE 'Farmer%' THEN 'Farmers Market'
        WHEN so.sales_channel ILIKE 'Amazon%' THEN 'Amazon'
        WHEN so.sales_channel ILIKE ANY(ARRAY['%Shopify%', '%Nexternal%']) THEN 'Online Store'
        ELSE so.sales_channel
    END as sales_channel_type,
    so.sales_channel as sales_channel_name,
    so.order_id,
    so.order_line_id,
    so.order_status,
    so.fulfillment_status,
    so.order_number,

    CASE 
        WHEN so.sales_channel LIKE 'Farmers Market%' AND so.product_sku IS NULL THEN 'Farmers Market Sales'
        WHEN so.sales_channel = 'Shopify Retail' AND so.product_sku IS NULL THEN 'Shopify Custom Sales'
        ELSE so.product_family
    END as product_family,
    CASE 
        WHEN so.sales_channel LIKE 'Farmers Market%' AND so.product_sku IS NULL THEN 'Farmers Market Sales'
        WHEN so.sales_channel = 'Shopify Retail' AND so.product_sku IS NULL THEN 'Shopify Custom Sales'
        ELSE so.product_category
    END as product_category,
    CASE 
        WHEN so.sales_channel LIKE 'Farmers Market%' AND so.product_sku IS NULL THEN 'Farmers Market Sales'
        WHEN so.sales_channel = 'Shopify Retail' AND so.product_sku IS NULL THEN 'Shopify Custom Sales'
        ELSE so.product_sku
    END as product_sku,
    CASE 
        WHEN so.sales_channel LIKE 'Farmers Market%' AND so.product_sku IS NULL THEN 'Farmers Market Sales' 
        WHEN so.sales_channel = 'Shopify Retail' AND so.product_sku IS NULL THEN 'Shopify Custom Sales' 
        ELSE so.product_description
    END as product_description,
    so.source_product_id,
    so.source_product_sku,
    so.source_product_name,
    so.quantity,
    (
        (COALESCE(so.net_sales, 0) / quantity)
    ) as unit_sales_price,
    (
        (COALESCE(so.material_cost, 0) / quantity)
    ) as unit_material_cost,
    (
        (COALESCE(so.direct_labor, 0) / quantity)
    ) as unit_direct_labor,
    (
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.adder_fullfilment_cost, 0)
    ) as unit_moondance_fulfillment_cost,
    (
        (
            COALESCE(so.sales_channel_fees, 0) +
            COALESCE(order_adder.adder_sales_channel_fees, 0)
          
        ) / quantity
    ) as unit_sales_channel_fees,
    (
		(
			COALESCE(so.material_cost, 0) +
			COALESCE(so.direct_labor, 0) +
			COALESCE(so.sales_channel_fees, 0) +
			COALESCE(so.shipping_cost, 0) +
			COALESCE(adder_line.labor_cost, 0) + 
			COALESCE(adder_line.material_cost, 0) +
			COALESCE(order_adder.adder_fullfilment_cost, 0) +
			COALESCE(order_adder.adder_sales_channel_fees, 0)
		) / quantity
    ) as unit_cost,
    NULLIF(so.net_sales, 0) as net_sales,
    so.shipping_collected,
    so.shipping_cost,
    (
        COALESCE(so.shipping_collected, 0) -
        COALESCE(so.shipping_cost, 0)
    ) as shipping_margin,
    so.material_cost,
    so.direct_labor,
    (
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.adder_fullfilment_cost, 0)
    ) as moondance_fulfillment_cost,
    (
        COALESCE(so.sales_channel_fees, 0) +
		COALESCE(order_adder.adder_sales_channel_fees, 0)
    ) as sales_channel_fees,
    (
        COALESCE(so.material_cost, 0) +
        COALESCE(so.direct_labor, 0) +
        COALESCE(so.sales_channel_fees, 0) +
        COALESCE(so.shipping_cost, 0) +
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.adder_fullfilment_cost, 0) +
		COALESCE(order_adder.adder_sales_channel_fees, 0)
    ) as product_cost,
    (
        COALESCE(so.net_sales, 0) -
        (
            COALESCE(so.material_cost, 0) +
            COALESCE(so.direct_labor, 0) +
            COALESCE(so.sales_channel_fees, 0) +
            COALESCE(adder_line.labor_cost, 0) +
            COALESCE(adder_line.material_cost, 0) +
            COALESCE(order_adder.adder_fullfilment_cost, 0) +
			COALESCE(order_adder.adder_sales_channel_fees, 0)
        )
    ) as product_margin,
    NULLIF(
        COALESCE(so.net_sales, 0) +
        COALESCE(so.shipping_collected, 0) -
        (
            COALESCE(so.material_cost, 0) +
            COALESCE(so.direct_labor, 0) +
            COALESCE(so.sales_channel_fees, 0) +
            COALESCE(so.shipping_cost, 0) +
            COALESCE(adder_line.labor_cost, 0) +
            COALESCE(adder_line.material_cost, 0) +
            COALESCE(order_adder.adder_fullfilment_cost, 0) +
			COALESCE(order_adder.adder_sales_channel_fees, 0)
        )
    , 0) as gross_profit,
    discount_promotion_name,
    total_discounts_given,
    customer_type,
    INITCAP(customer_name) as customer_name,
    company,
    ship_to_state,
    is_tax_exempt,
    date_created::DATE as date_created,
    date_last_updated::DATE as date_last_updated,
    processed_date::DATE as processed_date,
    processed_year,
    processed_month,
    processed_period,
    cost_type,
    1::NUMERIC /order_count.order_line_count::NUMERIC as order_count,
    CASE
        WHEN customer_type = 'Wholesale' OR so.source_system = 'Amazon' THEN NULL
        WHEN so.sales_channel = 'Farmers Market - Durham' THEN 'Durham County Tax'
        WHEN so.sales_channel = 'Farmers Market - Wake Forest' THEN 'Wake County Tax' 
        ELSE order_line_taxes.county
    END as county_tax_name,
    state_tax.state as state_tax_name,
    county_tax.transit_rate as county_transit_tax_rate,
    county_tax.base_rate as county_base_tax_rate,
    state_tax.base_rate as state_tax_rate,
    (county_tax.transit_rate/100::NUMERIC) * (COALESCE(so.net_sales, 0) + COALESCE(so.shipping_collected, 0)) as total_county_transit_tax,
    (county_tax.base_rate/100::NUMERIC)  * (COALESCE(so.net_sales, 0) + COALESCE(so.shipping_collected, 0)) as total_county_base_tax,
    (state_tax.base_rate/100::NUMERIC)  * (COALESCE(so.net_sales, 0) + COALESCE(so.shipping_collected, 0)) as total_state_tax,
    NULLIF(
        COALESCE(order_line_taxes.taxes_collected, 0) + 
        COALESCE(so.shipping_tax_collected, 0) 
    , 0) as taxes_collected,
    NULLIF(
        COALESCE(so.net_sales, 0) +
        COALESCE(so.shipping_collected, 0) +
        COALESCE(order_line_taxes.taxes_collected, 0) + 
        COALESCE(so.shipping_tax_collected, 0)
    , 0) as total_gross_sales
FROM
    sales_orders so LEFT JOIN
    adder_rates adder_line ON
        so.sales_channel = adder_line.sales_channel AND
        adder_line.apply_to = 'Each Order Line' LEFT JOIN
    order_adder ON
        so.sales_channel = order_adder.sales_channel AND
        so.order_id = order_adder.order_id LEFT JOIN
    order_count ON
        so.sales_channel = order_count.sales_channel AND
        so.order_id = order_count.order_id LEFT JOIN
    order_line_taxes ON 
        --so.source_system != 'Amazon' AND
        --so.customer_type = 'Retail' AND
        so.order_line_id = order_line_taxes.order_line_id LEFT JOIN
    public.accounting_tax_rate_county county_tax ON
        CASE
            WHEN customer_type = 'Wholesale' OR so.source_system = 'Amazon' THEN NULL
            WHEN so.sales_channel = 'Farmers Market - Durham' THEN 'Durham County Tax'
            WHEN so.sales_channel = 'Farmers Market - Wake Forest' THEN 'Wake County Tax' 
            ELSE order_line_taxes.county
        END = county_tax.county LEFT JOIN
    public.accounting_tax_rate_state state_tax ON county_tax.state_id = state_tax.id
;
