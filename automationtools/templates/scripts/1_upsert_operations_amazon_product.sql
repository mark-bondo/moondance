INSERT INTO public.integration_amazon_product (
    asin,
    product_id,
    sku_description,
    _active,
    _created,
    _last_updated,
    _created_by_id,
    _last_updated_by_id
)

SELECT 
    DISTINCT ON ("ASIN")
    "ASIN" as asin,
    NULL::INTEGER as product_id,
    "Title" as sku_description,
    TRUE as _active,
    NOW() as _created,
    NOW() as _last_updated,
    1 as _created_by_id,
    1 as _last_updated_by_id
FROM
    amazon.amazon_sales_order_line ol
ORDER BY
    "ASIN",
    "LastUpdateDate" DESC
ON CONFLICT (asin)
DO UPDATE
    SET
        sku_description = EXCLUDED.sku_description
;
