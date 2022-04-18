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
    _last_updated_by_id,
    costing_method
)

SELECT DISTINCT ON (shopify_sku)
    shop._active,
    NOW() as _created,
    NOW() as _last_updated,
    shopify_sku as sku,
    title as description,
    barcode as upc,
    'All' as sales_channel_type,
    'each' as unit_of_measure,
    "price" as unit_sales_price,
    1 as _created_by_id,
    1 as _last_updated_by_id,
    'No Cost Found'::TEXT as costing_method
FROM
    public.integration_shopify_product shop
WHERE
    title NOT ILIKE '%AMAZON%'
ORDER BY
    shopify_sku,
    shop._last_updated DESC NULLS LAST
ON CONFLICT (sku)
DO UPDATE
SET
    _last_updated = EXCLUDED._last_updated,
    sku = EXCLUDED.sku,
    description = EXCLUDED.description,
    upc = EXCLUDED.upc,
    sales_channel_type = EXCLUDED.sales_channel_type,
    unit_of_measure = EXCLUDED.unit_of_measure,
    unit_sales_price = EXCLUDED.unit_sales_price,
    _created_by_id = EXCLUDED._created_by_id,
    _last_updated_by_id = EXCLUDED._last_updated_by_id,
    _active = EXCLUDED._active
;
