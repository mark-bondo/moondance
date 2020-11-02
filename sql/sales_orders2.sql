WITH nexternal_shipping AS (
    SELECT
        order_number,
        GREATEST(SUM(extended_price)::NUMERIC / 25::NUMERIC, 1) AS fulfillment_factor,
        SUM(total_weight) AS total_weight,
        SUM(quantity) as order_quantity
    FROM
        public.sales_orders_nexternal
    GROUP BY
        order_number
)
, shipping_allocation AS (
    SELECT
        order_id as order_number,
        SUM(quantity)::NUMERIC as order_quantity,
        count(*)::NUMERIC as row_count
    FROM
        public.fees_amazon
    WHERE
        type = 'Order'
    GROUP BY
        order_id
)
, shipping_fees AS (
    SELECT
        order_id as order_number,
        sum(other) as shipping_fees
    FROM
        public.fees_amazon
    WHERE
        type = 'Shipping Services'
    GROUP BY
        order_id
)
, combined AS (
    SELECT
        'Platform: Nexternal'::TEXT as platform,
        so.order_status,
        'MoonDance Fulfullment' as fulfillment,
        so.order_number::VARCHAR as order_number,
        so.order_line,
        so.datetime_ordered,
        DATE_PART('YEAR', so.datetime_ordered)::INTEGER as order_year,
        DATE_PART('MONTH', so.datetime_ordered)::INTEGER as order_month,
        so.datetime_shipped,
        so.customer_type,
        so.product_category as marketing_category,
        COALESCE(item_master_nexternal.supply_chain_category, no_sku.supply_chain_category) as supply_chain_category,
        so.product_name as product_name_historical,
        item_master_nexternal.name as product_name_nexternal,
        (
            COALESCE(item_master_nexternal.supply_chain_name, no_sku.supply_chain_name) || 
            CASE WHEN COALESCE(item_master_nexternal.measure, no_sku.measure) IS NOT NULL THEN ' ' || COALESCE(item_master_nexternal.measure, no_sku.measure)::NUMERIC(16, 1)::TEXT || ' ' ELSE '' END ||
            CASE WHEN COALESCE(item_master_nexternal.unit_of_measure, no_sku.unit_of_measure) IS NOT NULL THEN COALESCE(item_master_nexternal.unit_of_measure, no_sku.unit_of_measure) ELSE '' END 
        ) as supply_chain_name,
        so.product_sku as nexternal_sku,
        NULL::TEXT as amazon_asin,
        so.product_attribute,
        so.quantity,
        so.extended_price as total_sales,
        (COALESCE(item_master_nexternal.unit_cost, no_sku.unit_cost) * so.quantity) as total_material_cost,
        (fulfillment_factor * (so.quantity::NUMERIC / nexternal_shipping.order_quantity::NUMERIC)) as total_fulfillment_cost,
        (
             (COALESCE(so.unit_price, 0) * so.quantity)
            -(COALESCE(item_master_nexternal.unit_cost, no_sku.unit_cost, 0) * so.quantity)
            -(fulfillment_factor * (so.quantity::NUMERIC / nexternal_shipping.order_quantity::NUMERIC))
        ) as total_margin,
        so.shipping_method,
        so.tracking_number,
        so.ship_to_state,
        so.unit_weight,
        so.total_weight
    FROM
        "public"."sales_orders_nexternal" so
        LEFT JOIN public.item_master_nexternal ON TRIM(so.product_sku) = TRIM(item_master_nexternal.sku)
        LEFT JOIN nexternal_shipping ON
            so.order_number = nexternal_shipping.order_number
        LEFT JOIN public.item_master_nexternal_no_sku no_sku ON 
            TRIM(so.product_name) = TRIM(no_sku.name) AND
            TRIM(COALESCE(so.product_attribute, '')) = TRIM(COALESCE(no_sku.attribute, ''))
    
    UNION ALL
    
    SELECT
        'Platform: Amazon'::TEXT as platform,
        'Shipped' as order_status,
        CASE
            WHEN fees.fulfillment = 'Seller' THEN 'MoonDance Fulfillment'
            ELSE 'FBA'
        END as fulfillment,
        fees.order_id as order_number,
        NULL::INTEGER as order_line,
        TO_TIMESTAMP(fees.date_time, 'Mon DD YYYY HH:MI:SS AM') at time zone 'PST' at time zone 'EST' as order_datetime,
        DATE_PART('YEAR', TO_TIMESTAMP(fees.date_time, 'Mon DD YYYY HH:MI:SS AM') at time zone 'PST' at time zone 'EST')::INTEGER as order_year,
        DATE_PART('MONTH', TO_TIMESTAMP(fees.date_time, 'Mon DD YYYY HH:MI:SS AM') at time zone 'PST' at time zone 'EST')::INTEGER as order_month,
        NULL::DATE as ship_date,
        'Consumer'::TEXT as customer_type,
        n.product_category as marketing_category,
        n.supply_chain_category,
        fees.description as product_name_historical,
        n.name as product_name_nexternal,
        (
            n.supply_chain_name || 
            CASE WHEN n.measure IS NOT NULL THEN ' ' || measure::NUMERIC(16, 1)::TEXT || ' ' ELSE '' END ||
            CASE WHEN n.unit_of_measure IS NOT NULL THEN unit_of_measure ELSE '' END 
        ) as supply_chain_name,
        n.sku as nexternal_sku,
        fees.sku as amazon_sku,
        NULL::TEXT as product_attribute,
        fees.quantity,
        fees.product_sales as total_sales,
        COALESCE(fees.quantity * n.unit_cost, 0) as total_material_cost,
       -(
              COALESCE(fees.fba_fees, 0) 
            + COALESCE(fees.selling_fees, 0) 
            + COALESCE(shipping_fees.shipping_fees / shipping_allocation.row_count, 0)
            - CASE
                WHEN fulfillment = 'Seller' THEN 1::NUMERIC * (fees.quantity::NUMERIC / shipping_allocation.order_quantity::NUMERIC)
                ELSE COALESCE(0.25::NUMERIC * fees.quantity::NUMERIC, 0) 
              END -- assumed fullfilment fee
        ) as total_fulfillment_cost,
        (
              COALESCE(fees.product_sales, 0)
            - COALESCE(fees.quantity * n.unit_cost, 0)
            + (
                  COALESCE(fees.fba_fees, 0) 
                + COALESCE(fees.selling_fees, 0) 
                + COALESCE(shipping_fees.shipping_fees / shipping_allocation.row_count, 0)
                - CASE
                    WHEN fulfillment = 'Seller' THEN 1::NUMERIC * (fees.quantity::NUMERIC / shipping_allocation.order_quantity::NUMERIC)
                    ELSE COALESCE(0.25::NUMERIC * fees.quantity::NUMERIC, 0) 
                  END -- assumed fullfilment fee
            )
        ) as total_margin,
        NULL::TEXT as shipping_method,
        NULL::TEXT as tracking_number,
        fees.order_state as ship_to_state,
        n.unit_weight,
        (n.unit_weight * fees.quantity)::NUMERIC(16, 2) as total_weight
    FROM
        "public"."fees_amazon" fees
        LEFT JOIN public.item_master_amazon a ON fees.sku = a.amazon_sku
        LEFT JOIN public.item_master_nexternal n ON COALESCE(a.nexternal_sku, fees.sku) = n.sku
        LEFT JOIN shipping_allocation ON fees.order_id = shipping_allocation.order_number
        LEFT JOIN shipping_fees ON fees.order_id = shipping_fees.order_number
    WHERE
        type IN ('Order')
)


SELECT
    CASE
        WHEN COALESCE(total_material_cost, 0) = 0 THEN 'Missing Cost'
        ELSE 'Costed'
    END as costing_status,
    platform,
    order_status,
    fulfillment,
    order_number,
    order_line,
    datetime_ordered,
    DATE_PART('YEAR', datetime_ordered)::INTEGER as order_year,
    DATE_PART('MONTH', datetime_ordered)::INTEGER as order_month,
    datetime_shipped,
    customer_type,
    marketing_category,
    supply_chain_category,
    product_name_historical,
    product_name_nexternal,
    supply_chain_name,
    nexternal_sku,
    amazon_asin,
    product_attribute,
    (total_sales / quantity)::NUMERIC(16, 2) AS unit_sale_price,
    (total_material_cost / quantity)::NUMERIC(16, 2) AS unit_material_cost,
    (total_fulfillment_cost / quantity)::NUMERIC(16, 2) AS unit_fulfillment_cost,
    (total_margin / quantity)::NUMERIC(16, 2) AS unit_margin,
    quantity::INTEGER as quantity,
    total_sales::NUMERIC(16, 2) AS total_sales,
    total_material_cost::NUMERIC(16, 2) AS total_material_cost,
    total_fulfillment_cost::NUMERIC(16, 2) AS total_fulfillment_cost,
    total_margin::NUMERIC(16, 2) AS total_margin,
    shipping_method,
    tracking_number,
    ship_to_state,
    unit_weight,
    total_weight
FROM
    combined
WHERE
    order_year >= 2019 AND
    order_number NOT LIKE 'S%' AND
    order_status NOT IN ('Canceled', 'Cancelled') AND
    COALESCE(supply_chain_category, '') != 'Packaging'