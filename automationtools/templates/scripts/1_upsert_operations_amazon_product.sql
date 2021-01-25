INSERT INTO public.operations_amazon_product (
    asin,
    product_id,
    seller_sku,
    sku_description,
    _active,
    _created,
    _last_updated,
    _created_by_id,
    _last_updated_by_id
)

SELECT 
    DISTINCT ON ("SellerSKU")
    "ASIN" as asin,
    NULL::INTEGER as product_id,
    "SellerSKU" as seller_sku,
    "Title" as sku_description,
    TRUE as _active,
    NOW() as _created,
    NOW() as _last_updated,
    1 as _created_by_id,
    1 as _last_updated_by_id
FROM
    amazon_sales_order_line ol
ORDER BY
    "SellerSKU",
    "LastUpdateDate" DESC
ON CONFLICT (seller_sku)
DO UPDATE
    SET
        asin = EXCLUDED.asin,
        sku_description = EXCLUDED.sku_description
;