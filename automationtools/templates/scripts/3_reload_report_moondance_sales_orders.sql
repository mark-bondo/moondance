/*
TODO
    add order level discounts
*/

CREATE TEMP TABLE default_costs ON COMMIT DROP AS
    SELECT 0.30::NUMERIC as percent
;


CREATE TEMP TABLE order_line_taxes ON COMMIT DROP AS
    WITH tax_detail AS (
        SELECT
            jsonb_array_elements(line_items)->>'id' as order_line_id,
            jsonb_array_elements(jsonb_array_elements(line_items)->'tax_lines')->>'title' as tax_types
        FROM
            shopify.shopify_sales_order
    )

    SELECT
        order_line_id::BIGINT as order_line_id,
        (ARRAY_REMOVE(ARRAY_AGG(DISTINCT tax_types ORDER BY tax_types), 'North Carolina State Tax'))[1] as county
    FROM
        tax_detail
    WHERE
        tax_types <> 'Sales tax'
    GROUP BY
        order_line_id::BIGINT
;


CREATE TEMP TABLE sales_orders ON COMMIT DROP AS
WITH shopify_line_items AS (
    SELECT
        jsonb_array_elements(line_items) as line_json,
        CASE
            WHEN source_name = 'sell-on-amazon' THEN 'Amazon FBM'
            WHEN source_name IN ('580111', 'web', 'shopify_draft_order') or customer->>'tags' LIKE '%wholesaler%' THEN 'Shopify Website'
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
        reference,
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
        )::NUMERIC(16, 2) as shipping_cost
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
            "AmazonOrderId",
            (jsonb_array_elements("ShipmentItemList")->>'OrderItemId')::BIGINT as "OrderItemId",
            jsonb_array_elements("ShipmentItemList")->>'SellerSKU' as "SellerSKU",
            -(jsonb_array_elements(jsonb_array_elements("ShipmentItemList")->'ItemFeeList')->'FeeAmount'->>'CurrencyAmount')::NUMERIC(16, 2) as fees
        FROM
            amazon.amazon_financial_events
    )

    SELECT
        "AmazonOrderId",
        "OrderItemId",
        i.product_id,
        SUM(fees) as total_fees
    FROM
        lines LEFT JOIN
        public.integration_amazon_product i ON lines."SellerSKU" = i.seller_sku
    WHERE
        fees != 0
    GROUP BY
        "AmazonOrderId",
        "OrderItemId",
        i.product_id

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
    CASE 
        WHEN sales_channel = 'POS' and p.sku IS NULL THEN 'POS Custom Sales' 
        WHEN sales_channel = 'Shopify Website' and p.sku IS NULL THEN 'Shopify Custom Sales' 
        ELSE pcode.family 
    END as product_family,
    CASE 
        WHEN sales_channel = 'POS' and p.sku IS NULL THEN 'POS Custom Sales' 
        WHEN sales_channel = 'Shopify Website' and p.sku IS NULL THEN 'Shopify Custom Sales' 
        ELSE pcode.category 
    END as product_category,
    CASE 
        WHEN sales_channel = 'POS' and p.sku IS NULL THEN 'POS Custom Sales' 
        WHEN sales_channel = 'Shopify Website' and p.sku IS NULL THEN 'Shopify Custom Sales' 
        ELSE p.sku 
    END as product_sku,
    CASE 
        WHEN sales_channel = 'POS' and p.sku IS NULL THEN 'POS Custom Sales' 
        WHEN sales_channel = 'Shopify Website' and p.sku IS NULL THEN 'Shopify Custom Sales' 
        ELSE p.description 
    END as product_description,
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
    ) as total_sales,
    shopify_shipping_allocation.shipping_collected as total_shipping_collected,
    shopify_shipping_allocation.shipping_cost as total_shipping_cost,
    (
        COALESCE(
            bundles.unit_material_cost, 
            p.unit_material_cost,
            (SELECT percent FROM default_costs) * (line_json->>'price')::NUMERIC
        ) *
        (
            (line_json->>'quantity')::NUMERIC - 
            COALESCE(refunds.quantity, 0)
        )
    ) as total_material_cost,
    NULL::NUMERIC as total_moondance_fulfillment_cost,
    amazon_fees.total_fees as total_amazon_fees,
    discount_applications->0->>'title' as discount_promotion_name,
    (line_json->'discount_allocations'->0->>'amount')::NUMERIC as total_discounts_given,
    CASE
        WHEN customer->>'tags' ILIKE '%wholesaler%' THEN 'Wholesale'
        ELSE 'Retail'
    END as customer_type,
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
    DATE_TRUNC('MONTH', processed_at::TIMESTAMP WITH TIME ZONE)::DATE as processed_period,
    CASE
        WHEN COALESCE(bundles.unit_material_cost, p.unit_material_cost) IS NULL THEN 'Product Cost'
        ELSE 'Average Cost'
    END as cost_type
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
    shopify_shipping_allocation ON (line_json->>'id') = shopify_shipping_allocation.order_line_id LEFT JOIN
    amazon_fees ON 
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
    (sl."ItemPrice"->>'Amount')::NUMERIC as total_sales,
    NULL::NUMERIC as total_shipping_collected,
    NULL::NUMERIC as total_shipping_cost,
    (
        COALESCE(
            COALESCE(bundles.unit_material_cost, product.unit_material_cost) * sl."QuantityOrdered",
            (SELECT percent FROM default_costs) * (sl."ItemPrice"->>'Amount')::NUMERIC
        )
    )::NUMERIC as total_material_cost,
    NULL::NUMERIC as total_moondance_fulfillment_cost,
    amazon_fees.total_fees::NUMERIC as total_amazon_fees,
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
        WHEN COALESCE(bundles.unit_material_cost, product.unit_material_cost) IS NULL THEN 'Product Cost'
        ELSE 'Average Cost'
    END as cost_type
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

CREATE TEMP TABLE order_count ON COMMIT DROP AS
    SELECT
        order_id,
        sales_channel,
        count(*) as order_line_count
    FROM
        sales_orders
    GROUP BY
        order_id,
        sales_channel

;


CREATE TEMP TABLE adder_rates ON COMMIT DROP AS
    SELECT
        sales_channel,
        apply_to,
        ARRAY_AGG(name::TEXT || ' - ' || labor_minutes::TEXT || ' minutes at ' || labor_hourly_rate || ' per hour') as overlay_description,
        SUM((labor_hourly_rate::NUMERIC/60::NUMERIC) * labor_minutes::NUMERIC) as labor_cost,
        SUM(material_cost) as material_cost
    FROM
        public.operations_order_cost_overlay
    GROUP BY
        sales_channel,
        apply_to
;


CREATE TEMP TABLE order_adder ON COMMIT DROP AS
    SELECT
        order_count.order_id,
        order_count.sales_channel,
        SUM((COALESCE(labor_cost, 0) + COALESCE(material_cost, 0)) / order_line_count) as cost_per_order
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
    unit_moondance_fulfillment_cost,
    unit_amazon_fees,
    unit_cost,
    total_sales,
    total_shipping_collected,
    total_shipping_cost,
    total_shipping_margin,
    total_material_cost,
    total_moondance_fulfillment_cost,
    total_amazon_fees,
    total_cost,
    total_product_margin,
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
    total_state_tax  
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
    (
        (COALESCE(total_sales, 0) / quantity)
    ) as unit_sales_price,
    (
        (COALESCE(total_material_cost, 0) / quantity)
    ) as unit_material_cost,
    (
        (COALESCE(total_moondance_fulfillment_cost, 0) / quantity) + 
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
    ) as unit_moondance_fulfillment_cost,
    (
        (COALESCE(total_amazon_fees, 0) / quantity)
    ) as unit_amazon_fees,
    (
		(
			COALESCE(total_material_cost, 0) +
			COALESCE(total_moondance_fulfillment_cost, 0) +
			COALESCE(total_amazon_fees, 0) +
			COALESCE(total_shipping_cost, 0) +
			COALESCE(adder_line.labor_cost, 0) + 
			COALESCE(adder_line.material_cost, 0) +
			COALESCE(order_adder.cost_per_order, 0)
		) / quantity
    ) as unit_cost,
    total_sales,
    total_shipping_collected,
    total_shipping_cost,
    (
        COALESCE(total_shipping_collected, 0) -
        COALESCE(total_shipping_cost, 0)
    ) as total_shipping_margin,
    total_material_cost,
    (
        COALESCE(total_moondance_fulfillment_cost, 0) +
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
    ) as total_moondance_fulfillment_cost,
    (
        COALESCE(total_amazon_fees, 0)
    ) as total_amazon_fees,
    (
        COALESCE(total_material_cost, 0) +
        COALESCE(total_moondance_fulfillment_cost, 0) +
        COALESCE(total_amazon_fees, 0) +
        COALESCE(total_shipping_cost, 0) +
        COALESCE(adder_line.labor_cost, 0) + 
        COALESCE(adder_line.material_cost, 0) +
        COALESCE(order_adder.cost_per_order, 0)
    ) as total_cost,
    (
        COALESCE(total_sales, 0) -
        (
            COALESCE(total_material_cost, 0) +
            COALESCE(total_moondance_fulfillment_cost, 0) +
            COALESCE(total_amazon_fees, 0) +
            COALESCE(adder_line.labor_cost, 0) +
            COALESCE(adder_line.material_cost, 0) +
            COALESCE(order_adder.cost_per_order, 0)
        )
    ) as total_product_margin,
    (
        COALESCE(total_sales, 0) +
        COALESCE(total_shipping_collected, 0) -
        (
            COALESCE(total_material_cost, 0) +
            COALESCE(total_moondance_fulfillment_cost, 0) +
            COALESCE(total_amazon_fees, 0) +
            COALESCE(total_shipping_cost, 0) +
            COALESCE(adder_line.labor_cost, 0) +
            COALESCE(adder_line.material_cost, 0) +
            COALESCE(order_adder.cost_per_order, 0)
        )
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
    processed_period,
    cost_type,
    1::NUMERIC /order_count.order_line_count::NUMERIC as order_count,
    CASE
        WHEN so.sales_channel = 'POS' THEN 'Durham County Tax' 
        ELSE order_line_taxes.county
    END as county_tax_name,
    state_tax.state as state_tax_name,
    county_tax.transit_rate as county_transit_tax_rate,
    county_tax.base_rate as county_base_tax_rate,
    state_tax.base_rate as state_tax_rate,
    (county_tax.transit_rate/100::NUMERIC) * (COALESCE(total_sales, 0) + COALESCE(total_shipping_collected, 0)) as total_county_transit_tax,
    (county_tax.base_rate/100::NUMERIC)  * (COALESCE(total_sales, 0) + COALESCE(total_shipping_collected, 0)) as total_county_base_tax,
    (state_tax.base_rate/100::NUMERIC)  * (COALESCE(total_sales, 0) + COALESCE(total_shipping_collected, 0)) as total_state_tax   
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
        so.source_system != 'Amazon' AND
        so.customer_type = 'Retail' AND
        so.order_line_id = order_line_taxes.order_line_id LEFT JOIN
    public.accounting_tax_rate_county county_tax ON
        CASE
            WHEN so.sales_channel = 'POS' THEN 'Durham County Tax' 
            ELSE order_line_taxes.county
        END = county_tax.county LEFT JOIN
    public.accounting_tax_rate_state state_tax ON county_tax.state_id = state_tax.id
;

 