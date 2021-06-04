INSERT INTO public.operations_product (
    _active,
    _created,
    _last_updated,
    sku,
    description,
    upc,
    sales_channel_type,
    unit_of_measure,
    unit_sales_price,
    _created_by_id,
    _last_updated_by_id
)

SELECT DISTINCT ON (shopify_sku)
    shop._active,
    NOW() as _created,
    NOW() as _last_updated,
    "shopify_sku" as sku,
    "title" as description,
    "barcode" as upc,
    'All' as sales_channel_type,
    'each' as unit_of_measure,
    "price" as unit_sales_price,
    1 as _created_by_id,
    1 as _last_updated_by_id
FROM
    public.integration_shopify_product shop LEFT JOIN
    public.operations_product p ON shop.shopify_sku = p.sku
WHERE
    p.id IS NULL AND
    shop.product_id IS NULL
ORDER BY
    shopify_sku,
    shop._last_updated DESC NULLS LAST
;
