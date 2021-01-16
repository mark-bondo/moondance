SELECT
-COALESCE((refunds->0->'transactions'->0->>'amount')::NUMERIC, 0),
*
FROM
    "public"."sales_orders_shopify"
WHERE
    --tax.id IS NULL AND
    test = FALSE AND
    COALESCE(source_name, '') <> 'sell-on-amazon' AND 
    processed_at::DATE BETWEEN '2020-11-01' AND '2020-11-30' and
        financial_status <> 'paid' 
--GROUP BY 1,2
