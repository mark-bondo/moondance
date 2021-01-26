INSERT INTO public.operations_product (
    _active,
    _created,
    _last_updated,
    sku,
    description,
    upc,
    unit_of_measure,
    unit_sales_price,
    _created_by_id,
    _last_updated_by_id,
    product_type
)

SELECT DISTINCT ON (shopify_sku)
    shop._active,
    NOW() as _created,
    NOW() as _last_updated,
    "shopify_sku" as sku,
    "title" as description,
    "barcode" as upc,
    'each' as unit_of_measure,
    "price" as unit_sales_price,
    1 as _created_by_id,
    1 as _last_updated_by_id,
    'Finished Goods' as product_type
FROM
    public.integration_shopify_product shop LEFT JOIN
    public.operations_product p ON shop.shopify_sku = p.sku
WHERE
    p.id isnull
ORDER BY
    shopify_sku,
    shop._last_updated DESC NULLS LAST
;