SELECT
    CASE
        WHEN tax_lines = '[]' THEN TRUE
        ELSE COALESCE((customer->>'tax_exempt')::BOOLEAN, FALSE)
    END as is_tax_exempt,
    CASE
        WHEN source_name = 'pos' AND shipping_address->>'province' IS NULL THEN 'North Carolina'
        WHEN shipping_address->>'province' IS NULL THEN 'North Carolina' -- pickup
        ELSE shipping_address->>'province'
    END as ship_to_state,
    SUM(total_price - COALESCE(total_tax, 0)) as total_sales_less_tax
FROM
    "public"."sales_orders_shopify"
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
GROUP BY
    1,2