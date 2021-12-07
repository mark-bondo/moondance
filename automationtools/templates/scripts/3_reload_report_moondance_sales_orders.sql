/*
TODO - add order level discounts
*/
CREATE TEMP TABLE shopify_so ON COMMIT DROP AS 
    SELECT
        so.id as order_id,
        so.name as order_number,
        CASE
            WHEN so.source_name = 'sell-on-amazon' THEN 'Amazon FBM'
            WHEN customer.tags ILIKE '%wholesale%' OR so.tags ILIKE '%wholesale%' THEN 'Wholesale'
            WHEN so.location_id = '61831086229' THEN 'Farmers Market - Wake Forest'
            WHEN 
                (so.source_name IN ('android', 'pos', 'iphone') AND EXTRACT('DOW' FROM so.processed_at::DATE) = 6) 
                OR 
                so.location_id = '61830463637'
                THEN 'Farmers Market - Durham'
            WHEN so.source_name IN ('279941', '580111', 'web', 'shopify_draft_order', 'android', 'pos', 'iphone') THEN 'Online Retail'
            ELSE so.source_name
        END as sales_channel_name,
        CASE
            WHEN so.financial_status IN ('pending') THEN so.financial_status
            WHEN so.fulfillment_status IN ('fulfilled') THEN so.fulfillment_status
            ELSE 'pending'
        END as order_status,
        so.line_items,
        so.shipping_lines,
        so.total_shipping_price_set,
        so.customer->>'id' as customer_id,
        so.closed_at as date_closed,
        so.created_at as date_created,
        so.updated_at as date_last_updated,
        so.processed_at as date_processed,
        so.shipping_address->>'province' as ship_to_state,
        so.tags
    FROM
        shopify.shopify_sales_order so
        LEFT JOIN shopify.shopify_customer customer ON so.customer->>'id' = customer.id::TEXT
    WHERE
        so.financial_status NOT IN ('voided', 'refunded') AND
        so.source_name <> 'sell-on-amazon'
;


CREATE TEMP TABLE taxes ON COMMIT DROP AS 
    WITH tax_base AS (
        SELECT
            order_id,
            JSONB_ARRAY_ELEMENTS(line_items)->>'id' as order_line_id,
            JSONB_ARRAY_ELEMENTS(JSONB_ARRAY_ELEMENTS(line_items)->'tax_lines') as tax_lines
        FROM
            shopify_so
        UNION ALL
        
        SELECT
            order_id,
            NULL::TEXT as order_line_id,
            JSONB_ARRAY_ELEMENTS((JSONB_ARRAY_ELEMENTS(shipping_lines)->'tax_lines')) as tax_lines
        FROM
            shopify_so
    )

    SELECT
        'County Tax' as tax_type,
        order_id::TEXT as order_id,
        order_line_id,
        tax_lines->>'title' as title,
        CASE
            WHEN (tax_lines->>'rate')::NUMERIC = 0.0200 THEN (tax_lines->>'rate')::NUMERIC
            WHEN (tax_lines->>'rate')::NUMERIC = 0.0225 THEN (tax_lines->>'rate')::NUMERIC
            WHEN (tax_lines->>'rate')::NUMERIC = 0.0250 THEN 0.0200
            WHEN (tax_lines->>'rate')::NUMERIC = 0.0275 THEN (tax_lines->>'rate')::NUMERIC
        END as base_rate,
        SUM(
            CASE
                WHEN (tax_lines->>'rate')::NUMERIC = 0.0200 THEN 0.0000
                WHEN (tax_lines->>'rate')::NUMERIC = 0.0225 THEN 0.0000
                WHEN (tax_lines->>'rate')::NUMERIC = 0.0250 THEN 0.0500
                WHEN (tax_lines->>'rate')::NUMERIC = 0.0275 THEN 0.0500
            END 
        ) as transit_rate,        
        SUM((tax_lines->>'price')::NUMERIC) AS amount
    FROM
        tax_base
    WHERE
        tax_lines->>'title' LIKE '% County %'
    GROUP BY
        2,3,4,5
        
    UNION ALL
    
    SELECT
        'State Tax' as tax_type,
        order_id::TEXT as order_id,
        order_line_id,
        tax_lines->>'title' as title,
        (tax_lines->>'rate')::NUMERIC as base_rate,
        NULL::NUMERIC as transit_rate,        
        SUM((tax_lines->>'price')::NUMERIC) AS amount
    FROM
        tax_base
    WHERE
        tax_lines->>'title' = 'North Carolina State Tax'
    GROUP BY
        2,3,4,5
;


CREATE TEMP TABLE combined ON COMMIT DROP AS 
WITH shopify_line_items AS (
    /* PRODUCTS */
    SELECT
        order_id,
        order_number,
        sales_channel_name,
        JSONB_ARRAY_ELEMENTS(line_items) as line_json,
        date_closed,
        date_created,
        date_last_updated,
        date_processed,
        order_status,
        ship_to_state,
        tags,
        customer_id
    FROM
        shopify_so

    UNION ALL
    
    /* SHIPPING */
    SELECT
        so.order_id,
        so.order_number,
        so.sales_channel_name,
        JSONB_BUILD_OBJECT(
            'id', NULL::BIGINT,
            'variant_id', NULL::BIGINT,
            'sku', 'Shipping',
            'name', 'Shipping',
            'quantity', NULL::INTEGER,
            'price', NULLIF((so.total_shipping_price_set->'shop_money'->>'amount')::NUMERIC, 0),
            'cost', NULLIF(COALESCE(shipping_cost.amount, 0) + COALESCE(shipping_easy.amount, 0), 0)
        ) as line_json,
        so.date_closed,
        so.date_created,
        so.date_last_updated,
        so.date_processed,
        so.order_status,
        so.ship_to_state,
        so.tags,
        so.customer_id
    FROM
        shopify_so so
        LEFT JOIN (
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
        ) shipping_cost ON so.order_id = shipping_cost.order_id
        LEFT JOIN (
            SELECT
                '#' || "Order Number" as order_number,
                SUM("Postage Cost")::NUMERIC(16, 2) as amount
            FROM
                shopify.shipping_easy_orders
            GROUP BY
                1
        ) shipping_easy ON so.order_number = shipping_easy.order_number 
    WHERE
        (
            COALESCE((total_shipping_price_set->'shop_money'->>'amount')::NUMERIC, 0) <> 0
                OR
            COALESCE(shipping_cost.amount, 0) + COALESCE(shipping_easy.amount, 0) <> 0 
        )
)
, shopify_discounts AS (
    WITH detail AS (
        SELECT
            line_json->>'id' as order_line_id,
            (JSONB_ARRAY_ELEMENTS(line_json->'discount_allocations')->>'amount')::NUMERIC as amount
        FROM
            shopify_line_items
        WHERE
            JSONB_ARRAY_LENGTH(line_json->'discount_allocations') > 0
    )
    
    SELECT
        order_line_id,
        SUM(amount) as amount
    FROM
        detail
    GROUP BY
        order_line_id
)
, amazon_events AS (
    WITH events AS (
        SELECT
            "FinancialEvents" as event,
            "AmazonOrderId" as order_id,
            "PostedDate" as date_processed,
            (jsonb_array_elements("ShipmentItemList")->>'QuantityShipped')::INTEGER as quantity,
            (jsonb_array_elements("ShipmentItemList")->>'OrderItemId')::BIGINT as order_line_id,
            jsonb_array_elements(jsonb_array_elements("ShipmentItemList")->'ItemFeeList') as item_fee_list,
            jsonb_array_elements(jsonb_array_elements("ShipmentItemList")->'ItemChargeList') as item_charge_list
        FROM
            amazon.amazon_financial_events
          --  WHERE "AmazonOrderId" = '111-0310293-0325000'

        UNION ALL

        SELECT
            "FinancialEvents" as event,
            "AmazonOrderId" as order_id,
            "PostedDate" as date_processed,
            -(jsonb_array_elements("ShipmentItemAdjustmentList")->>'QuantityShipped')::INTEGER as quantity,
            (jsonb_array_elements("ShipmentItemAdjustmentList")->>'OrderAdjustmentItemId')::BIGINT as order_line_id,
            jsonb_array_elements(jsonb_array_elements("ShipmentItemAdjustmentList")->'ItemFeeAdjustmentList') as item_fee_list,
            jsonb_array_elements(jsonb_array_elements("ShipmentItemAdjustmentList")->'ItemChargeAdjustmentList') as item_charge_list
        FROM
            amazon.amazon_financial_events_refunds
           -- WHERE 0=1--"AmazonOrderId" = '112-1029827-9418614'
    )

    SELECT
        --events.item_fee_list->>'FeeType' as fee_type,
        --events.item_charge_list->>'ChargeType' as charge_type,
        events.event,
        events.order_id,
        events.order_line_id,
        events.date_processed,
        sh."FulfillmentChannel" as fulfillment_channel,
        sh."OrderStatus" as order_status,
        sl."ASIN" as product_id,
        sl."SellerSKU" as product_sku,
        sl."Title" as product_description_full,
        sh._created as date_created,
        sh."LastUpdateDate" as date_last_updated,
        NULLIF(events.quantity, 0)::NUMERIC as quantity,
        SUM(
            CASE
                WHEN events.item_charge_list->>'ChargeType' NOT ILIKE ALL(ARRAY['%tax%', 'gift%', 'ShippingCharge']) THEN (events.item_charge_list->'ChargeAmount'->>'CurrencyAmount')::NUMERIC 
            END
        ) as net_sales,
        SUM(
            CASE
                WHEN events.item_charge_list->>'ChargeType' = 'ShippingCharge' THEN (events.item_charge_list->'ChargeAmount'->>'CurrencyAmount')::NUMERIC 
            END
        ) as shipping_collected,
        SUM(
            CASE
                WHEN events.item_charge_list->>'ChargeType' = 'ShippingTax' THEN (events.item_charge_list->'ChargeAmount'->>'CurrencyAmount')::NUMERIC 
            END
        ) as tax_collected_shipping,
        SUM(
            CASE
                WHEN events.item_charge_list->>'ChargeType' ILIKE '%tax%' AND events.item_charge_list->>'ChargeType' NOT ILIKE ALL(ARRAY['%shipping%', 'gift%']) THEN (events.item_charge_list->'ChargeAmount'->>'CurrencyAmount')::NUMERIC 
            END
        ) as tax_collected_state,
        -SUM(
            (events.item_fee_list->'FeeAmount'->>'CurrencyAmount')::NUMERIC
        ) as sales_channel_fees
    FROM
        events
        LEFT JOIN amazon.amazon_sales_order_line sl ON events.order_line_id = sl."OrderItemId"
        LEFT JOIN amazon.amazon_sales_order sh ON sl."AmazonOrderId" = sh."AmazonOrderId"
        LEFT JOIN public.integration_amazon_product i ON sl."ASIN" = i.asin
    WHERE
        COALESCE(events.item_fee_list->'FeeAmount'->>'CurrencyAmount', '0')::NUMERIC <> 0
        OR
        COALESCE(events.item_charge_list->'ChargeAmount'->'CurrencyAmount', '0')::NUMERIC <> 0
    GROUP BY
        --events.item_fee_list->>'FeeType',
        --events.item_charge_list->>'ChargeType',
        events.quantity,
        events.event,
        events.order_id,
        events.order_line_id,
        events.date_processed,
        sh."FulfillmentChannel",
        sh."OrderStatus",
        sl."ASIN",
        sl."SellerSKU",
        sl."Title",
        sh._created,
        sh."LastUpdateDate"
)

/* REFUNDS */
SELECT
    'Shopify' as source_system,
    so.sales_channel_name,
    so.order_id::TEXT as order_id,
    line_json->>'id' as order_line_id,
    so.order_status,
    so.order_number,
    (line_json->>'variant_id') as product_id,
    (line_json->>'sku') as product_sku,
    (line_json->>'name') as product_description_full,
    -(refunds.refund_line_items->>'quantity')::NUMERIC as quantity,
    -(refunds.refund_line_items->>'subtotal')::NUMERIC as net_sales,
    NULL::NUMERIC as tax_collected_state,
    NULL::NUMERIC as sales_channel_fees,
    so.ship_to_state,
    refunds.created_at as date_created,
    so.date_last_updated,
    refunds.processed_at::DATE as date_processed,
    so.tags,
    so.customer_id
FROM
    shopify_line_items so
    JOIN (
        SELECT
            created_at,
            processed_at,
            (
                JSONB_ARRAY_ELEMENTS(
                    (JSONB_ARRAY_ELEMENTS(refunds)->'refund_line_items')
                )
             ) as refund_line_items
        FROM
            shopify.shopify_sales_order
    ) refunds ON so.line_json->>'id' = refunds.refund_line_items->'line_item'->>'id'
 
UNION ALL

/* SALES */
SELECT
    'Shopify' as source_system,
    CASE
        WHEN (line_json->>'sku') = 'Shipping' THEN 'Shipping Collected'
        ELSE so.sales_channel_name
    END as sales_channel_name,
    so.order_id::TEXT as order_id,
    line_json->>'id' as order_line_id,
    so.order_status,
    so.order_number,
    (line_json->>'variant_id') as product_id,
    (line_json->>'sku') as product_sku,
    (line_json->>'name') as product_description_full,
    (line_json->>'quantity')::INTEGER as quantity,
    (
        (
            (line_json->>'price')::NUMERIC -
            COALESCE(discounts.amount / (line_json->>'quantity')::NUMERIC, 0)
        ) * COALESCE((line_json->>'quantity')::NUMERIC, 1::NUMERIC)
    ) as net_sales,
    NULL::NUMERIC as tax_collected_state,
    NULL::NUMERIC as sales_channel_fees,
    so.ship_to_state,
    so.date_created,
    so.date_last_updated,
    so.date_processed::DATE as date_processed,
    so.tags,
    so.customer_id
FROM
    shopify_line_items so
    LEFT JOIN shopify_discounts discounts ON (line_json->>'id') = discounts.order_line_id 

UNION ALL

/* SALES */
SELECT
    'Amazon' as source_system,
    CASE
        WHEN fulfillment_channel = 'AFN' THEN 'Amazon FBA'
        WHEN fulfillment_channel = 'MFN' THEN 'Amazon FBM'
    END as sales_channel_name,
    order_id,
    order_line_id::TEXT as order_line_id,
    CASE
        WHEN order_status IN ('Pending', 'Unshipped') THEN 'pending'
        WHEN order_status IN ('Shipped') THEN 'shipped'
    END as order_status,
    order_id as order_number,
    product_id,
    product_sku,
    product_description_full,
    quantity,
    net_sales,
    tax_collected_state,
    sales_channel_fees,
    NULL::TEXT as ship_to_state,
    date_created,
    date_last_updated,
    date_processed::DATE as date_processed,
    NULL::TEXT as tags,
    NULL::TEXT as customer_id
FROM
    amazon_events
WHERE
    COALESCE(net_sales, 0) IS NOT NULL
    OR
    COALESCE(sales_channel_fees, 0) IS NOT NULL
    OR
    COALESCE(tax_collected_state, 0) IS NOT NULL

UNION ALL

/* SHIPPING */
SELECT
    'Amazon' as source_system,
    CASE
        WHEN fulfillment_channel = 'AFN' THEN 'Amazon FBA'
        WHEN fulfillment_channel = 'MFN' THEN 'Amazon FBM'
    END as sales_channel_name,
    order_id,
    order_line_id::TEXT as order_line_id,
    CASE
        WHEN order_status IN ('Pending', 'Unshipped') THEN 'pending'
        WHEN order_status IN ('Shipped') THEN 'shipped'
    END as order_status,
    order_id as order_number,
    'Shipping'::TEXT as product_id,
    'Shipping'::TEXT as product_sku,
    'Shipping'::TEXT as product_description_full,
    NULL::NUMERIC as quantity,
    shipping_collected as net_sales,
    tax_collected_shipping as tax_collected_state,
    0::NUMERIC as sales_channel_fees,
    NULL::TEXT as ship_to_state,
    date_created,
    date_last_updated,
    date_processed::DATE as date_processed,
    NULL::TEXT as tags,
    NULL::TEXT as customer_id
FROM
    amazon_events
WHERE
    COALESCE(shipping_collected, 0) IS NOT NULL
;


TRUNCATE TABLE report_moondance.sales_order;
INSERT INTO report_moondance.sales_order (
    source_system,
    sales_channel_name,
    sales_channel_type,
    order_id,
    order_line_id,
    order_status,
    order_number,
    product_id,
    product_sku,
    product_description_full,
    product_description,
    product_family,
    product_subfamily,
    sales_channel_fees,
    customer_type,
    customer_name,
    company_name,
    ship_to_state,
    is_tax_exempt,
    date_created,
    date_last_updated,
    date_processed,
    processed_year,
    processed_month,
    processed_week,
    processed_period,
    tax_name_county,
    tax_name_state,
    tax_rate_transit,
    tax_rate_county,
    tax_rate_state,
    tax_collected_transit,
    tax_collected_county,
    tax_collected_state,
    quantity,
    unit_sales_price,
    net_sales,
    sales_tax,
    gross_sales
)

SELECT
    so.source_system,
    so.sales_channel_name,
    CASE
        WHEN so.sales_channel_name ILIKE 'Farmer%' THEN 'Farmers Market'
        WHEN so.sales_channel_name ILIKE 'Amazon%' THEN 'Amazon'
        WHEN so.sales_channel_name ILIKE ANY(ARRAY['%Shopify%', '%Nexternal%']) THEN 'Online Retail'
        ELSE so.sales_channel_name
    END as sales_channel_type,
    so.order_id,
    so.order_line_id,
    so.order_status,
    so.order_number,
    so.product_id,
    so.product_sku,
    so.product_description_full,
    COALESCE(product.description, so.product_description_full) as product_description,
    CASE 
        WHEN so.sales_channel_name LIKE 'Farmers Market%' AND so.product_sku IS NULL THEN 'Farmers Market Sales'
        WHEN so.sales_channel_name = 'Shopify Retail' AND so.product_sku IS NULL THEN 'Custom Sale'
        ELSE pcode.family
    END as product_family,
    CASE 
        WHEN so.sales_channel_name LIKE 'Farmers Market%' AND so.product_sku IS NULL THEN 'Farmers Market Sales'
        WHEN so.sales_channel_name = 'Shopify Retail' AND so.product_sku IS NULL THEN 'Custom Sale'
        ELSE pcode.category
    END as product_subfamily,
    so.sales_channel_fees,
    CASE
        WHEN customer.tags ILIKE '%wholesale%' OR so.tags ILIKE '%wholesale%' THEN 'Wholesale'
        ELSE 'Retail'
    END as customer_type,
    INITCAP(customer.first_name || ' ' || customer.last_name) as customer_name,
    COALESCE(
        NULLIF(customer.default_address->>'company', ''), 
        CASE 
            WHEN customer.tags ILIKE '%wholesale%' OR so.tags ILIKE '%wholesale%' THEN customer.first_name || ' ' || customer.last_name
        END
    ) as company_name,
    CASE
        WHEN so.sales_channel_name LIKE 'Farmers Market%' AND COALESCE(so.ship_to_state, customer.default_address->>'province_code') IS NULL THEN 'North Carolina'
        WHEN so.sales_channel_name NOT LIKE 'Amazon%' AND COALESCE(so.ship_to_state, customer.default_address->>'province_code') IS NULL THEN 'North Carolina' -- pickup
        WHEN ship_to_state = 'NC' OR customer.default_address->>'province_code' = 'NC' THEN 'North Carolina'
        ELSE COALESCE(so.ship_to_state, customer.default_address->>'province_code')
    END as ship_to_state,
    COALESCE(customer.tax_exempt, FALSE) as is_tax_exempt,
    date_created::DATE as date_created,
    date_last_updated::DATE as date_last_updated,
    date_processed::DATE as date_processed,
    DATE_PART('YEAR', date_processed)::INTEGER as processed_year,
    DATE_PART('MONTH', date_processed)::INTEGER as processed_month,
    DATE_PART('WEEK', date_processed)::INTEGER as processed_week,
    DATE_TRUNC('MONTH', date_processed)::DATE as processed_period,
    county_tax.title as tax_name_county,
    state_tax.title as tax_name_state,
    county_tax.transit_rate as tax_rate_transit,
    county_tax.base_rate as tax_rate_county,
    state_tax.base_rate as tax_rate_state,
    (
        county_tax.transit_rate /
        (COALESCE(county_tax.transit_rate, 0) + COALESCE(county_tax.base_rate, 0))
        
    ) * county_tax.amount as tax_collected_transit,
    (
        county_tax.base_rate /
        (COALESCE(county_tax.transit_rate, 0) + COALESCE(county_tax.base_rate, 0))
        
    ) * county_tax.amount as tax_collected_county,
    state_tax.amount as tax_collected_state,
    so.quantity,
    NULLIF(COALESCE(so.net_sales, 0) / NULLIF(quantity, 0), 0) as unit_sales_price,
    NULLIF(so.net_sales, 0) as net_sales,
    NULLIF(
        COALESCE(county_tax.amount, 0) +
        COALESCE(state_tax.amount, 0)
    , 0) as sales_tax,
    NULLIF(
        COALESCE(so.net_sales, 0) +
        COALESCE(county_tax.amount, 0) +
        COALESCE(state_tax.amount, 0)
    , 0) as gross_sales
FROM
    combined so 
    LEFT JOIN shopify.shopify_customer customer ON so.customer_id = customer.id::TEXT
    LEFT JOIN taxes county_tax ON
        CASE 
            WHEN so.product_sku = 'Shipping' THEN so.order_id 
            ELSE so.order_line_id 
        END = COALESCE(county_tax.order_line_id, county_tax.order_id) AND
        so.source_system = 'Shopify' AND
        county_tax.tax_type = 'County Tax'
    LEFT JOIN taxes state_tax ON
        CASE 
            WHEN so.product_sku = 'Shipping' THEN so.order_id 
            ELSE so.order_line_id 
        END = COALESCE(state_tax.order_line_id, state_tax.order_id) AND
        so.source_system = 'Shopify' AND
        state_tax.tax_type = 'State Tax'
    LEFT JOIN public.integration_amazon_product amazon_product ON
        so.product_id = amazon_product.asin AND
        so.sales_channel_name LIKE 'Amazon%'
    LEFT JOIN public.integration_shopify_product shopify_product ON 
        so.product_id = shopify_product.variant_id::TEXT AND
        so.sales_channel_name NOT LIKE 'Amazon%'
    LEFT JOIN public.integration_product_missing_sku missing ON
        so.product_description_full = missing.product_description AND
        so.source_system = missing.source_system
    LEFT JOIN public.operations_product product ON 
        COALESCE(amazon_product.product_id, shopify_product.product_id, missing.product_id) = product.id
        OR
        (
            COALESCE(amazon_product.product_id, shopify_product.product_id, missing.product_id) IS NULL AND
            so.product_sku = product.sku
        )
    LEFT JOIN public.operations_product_code pcode ON product.product_code_id = pcode.id 
;
