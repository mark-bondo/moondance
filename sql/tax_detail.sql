WITH line_items AS (		
    SELECT		
            "name",		
           -- "tax_lines",		
        jsonb_array_elements(
            CASE
                WHEN tax_lines = '[]' THEN '[{"title": "Tax Exempt", "price": 0.00, "rate":0}]'
                ELSE tax_lines
            END::JSONB
        ) as tax_lines,		
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
        "total_tax_set"	,
        COALESCE((customer->>'tax_exempt')::BOOLEAN, FALSE) as is_tax_exempt,
        CASE		
            WHEN source_name IN ('android', 'pos') AND shipping_address->>'province' IS NULL THEN 'North Carolina'		
            WHEN shipping_address->>'province' IS NULL THEN 'North Carolina' -- pickup		
            WHEN shipping_address->>'province' = 'NC' THEN 'North Carolina'
            ELSE shipping_address->>'province'		
        END as ship_to_state,		
        CASE		
            WHEN source_name = '580111' THEN 'web'	
            WHEN source_name = 'android' THEN 'pos'	
            ELSE source_name		
        END,
        (total_price::NUMERIC - COALESCE(total_tax, 0)::NUMERIC) - COALESCE((refunds->0->'transactions'->0->>'amount')::NUMERIC, 0) as total_sales_less_tax
    FROM		
        "public"."sales_orders_shopify"	

)		
			
SELECT	
    source_name,		
    line_items.name as order_number,		
    ship_to_state,				
    financial_status,		
    is_tax_exempt, 		
    total_sales_less_tax,			
    CASE		
        WHEN is_tax_exempt = FALSE AND source_name = 'pos' THEN 'Durham County Tax' 
        WHEN is_tax_exempt = TRUE THEN 'Tax Exempt'
        ELSE tax_lines->>'title'		
    END as tax_type,		
    county_tax.base_rate as county_tax_base_rate,			
    (total_sales_less_tax * (county_tax.base_rate::NUMERIC/100::NUMERIC))::NUMERIC(16, 2) as county_base_tax_due,		
    (total_sales_less_tax * (county_tax.transit_rate::NUMERIC/100::NUMERIC))::NUMERIC(16, 2) as county_transit_tax_tax_due,		
    (total_sales_less_tax * (state_tax.base_rate::NUMERIC/100::NUMERIC))::NUMERIC(16, 2) as state_tax_due,	
    shipping_address->>'name' as ship_to_name,		
    shipping_address->>'address1' as ship_to_address_1,		
    shipping_address->>'city' as ship_to_city,		
    shipping_address->>'zip' as ship_to_zip,		
    shipping_address->>'province' as ship_to_province,		
    shipping_address->>'country' as ship_to_country,				
    processed_at		
FROM		
    line_items LEFT JOIN		
    public.sales_tax_county_rates county_tax ON 		
        is_tax_exempt = FALSE AND
        CASE		
           WHEN source_name = 'pos' THEN 'Durham County Tax' 		
           ELSE tax_lines->>'title'		
        END = county_tax.name LEFT JOIN		
    public.sales_tax_state_rates state_tax ON 
        is_tax_exempt = FALSE AND
        ship_to_state = state_tax.name
WHERE		
    test = FALSE AND		
    COALESCE(tax_lines->>'title', '') <> 'North Carolina State Tax' AND
    COALESCE(source_name, '') <> 'sell-on-amazon' AND		
    financial_status IN ('paid', 'partially_refunded') AND			
    processed_at::DATE BETWEEN '2020-11-01' AND '2020-11-30'	
  		
