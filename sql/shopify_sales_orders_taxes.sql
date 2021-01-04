WITH line_items AS (
    SELECT
            "name",
           -- "tax_lines",
        jsonb_array_elements(tax_lines) as tax_lines,
        "fulfillments",
        "refunds",
        "total_tip_received",
        "original_total_duties_set",
        "current_total_duties_set",
        "admin_graphql_api_id",
        "shipping_lines",
        "billing_address",
        "client_details",
        "payment_details",
        "customer",
        "shipping_address",
        "id",
        "email",
        "closed_at",
        "created_at",
        "updated_at",
        "number",
        "note",
        "token",
        "gateway",
        "test",
        "total_price",
        "subtotal_price",
        "total_weight",
        "total_tax",
        "taxes_included",
        "currency",
        "financial_status",
        "confirmed",
        "total_discounts",
        "total_line_items_price",
        "cart_token",
        "buyer_accepts_marketing",
        "referring_site",
        "landing_site",
        "cancelled_at",
        "cancel_reason",
        "total_price_usd",
        "checkout_token",
        "reference",
        "user_id",
        "location_id",
        "source_identifier",
        "source_url",
        "processed_at",
        "device_id",
        "phone",
        "customer_locale",
        "app_id",
        "browser_ip",
        "landing_site_ref",
        "order_number",
        "discount_applications",
        "discount_codes",
        "note_attributes",
        "payment_gateway_names",
        "processing_method",
        "checkout_id",
        "source_name",
        "fulfillment_status",
        "tags",
        "contact_email",
        "order_status_url",
        "presentment_currency",
        "total_line_items_price_set",
        "total_discounts_set",
        "total_shipping_price_set",
        "subtotal_price_set",
        "total_price_set",
        "total_tax_set"
    FROM
        "public"."sales_orders_shopify"
)

--, taxes AS (
SELECT
    CASE
        WHEN source_name = '580111' THEN 'web'
        ELSE source_name
    END as source_name,
    line_items.name as order_number,
    CASE
        WHEN source_name = 'pos' AND shipping_address->>'province' IS NULL THEN 'North Carolina'
        WHEN shipping_address->>'province' IS NULL THEN 'North Carolina' -- pickup
        ELSE shipping_address->>'province'
    END as ship_to_state,
    fulfillment_status as order_fulfillment_status,   
    financial_status,
    customer->>'tax_exempt' as is_tax_exempt, 
    taxes_included,
    
    --TAXES
    total_price - COALESCE(total_tax, 0) as total_sales_less_tax,
    --tax_lines->>'rate' as tax_rate,
    CASE
        WHEN source_name = 'pos' AND tax_lines->>'title' = 'Wake County Tax' THEN 'Durham County Tax' 
        ELSE tax_lines->>'title'
    END as tax_type,
    county_tax.base_rate as county_tax_base_rate,
    county_tax.transit_rate as county_tax_transit_rate,
    (
        (total_price::NUMERIC - COALESCE(total_tax, 0)::NUMERIC) * (county_tax.base_rate::NUMERIC/100::NUMERIC)
    )::NUMERIC(16, 2) as county_base_tax_due,
    (
        (total_price::NUMERIC - COALESCE(total_tax, 0)::NUMERIC) * (county_tax.transit_rate::NUMERIC/100::NUMERIC)
    )::NUMERIC(16, 2) as county_transit_tax_tax_due,
    (
        (total_price::NUMERIC - COALESCE(total_tax, 0)::NUMERIC) * (state_tax.base_rate::NUMERIC/100::NUMERIC)
    )::NUMERIC(16, 2) as state_tax_due,
    
    
    --SHIPPING
    shipping_address->>'name' as ship_to_name,
    shipping_address->>'company' as ship_to_company,
    shipping_address->>'address1' as ship_to_address_1,
    shipping_address->>'city' as ship_to_city,
    shipping_address->>'zip' as ship_to_zip,
    shipping_address->>'province' as ship_to_province,
    shipping_address->>'country' as ship_to_country,
    shipping_address->>'phone' as ship_to_phone,
    
    --KEY DATES
    created_at,
    updated_at,
    cancelled_at,
    processed_at
FROM
    line_items LEFT JOIN
    public.sales_tax_county_rates county_tax ON 
        CASE
            WHEN source_name = 'pos' AND tax_lines->>'title' = 'Wake County Tax' THEN 'Durham County Tax' 
            ELSE tax_lines->>'title'
        END = county_tax.name LEFT JOIN
    public.sales_tax_state_rates state_tax ON tax_lines->>'title' = state_tax.name
WHERE
    --tax.id IS NULL AND
    test = FALSE AND
    COALESCE(source_name, '') <> 'sell-on-amazon' AND
    financial_status = 'paid' AND
    (
        shipping_address->>'province' IN ('North Carolina', 'NC')
        OR
        shipping_address->>'province' IS NULL
    ) AND
    processed_at::DATE BETWEEN '2020-10-01' AND '2020-10-31'
  
  



