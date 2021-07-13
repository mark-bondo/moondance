INSERT INTO public.integration_shopify_product (
    shopify_id,
    variant_id,
    shopify_sku,
    status,
    title,
    inventory_policy,
    inventory_management,
    grams,
    price,
    inventory_quantity,
    customer_type,
    barcode,
    tags,
    handle,
    _active,
    _created,
    _last_updated,
    _created_by_id,
    _last_updated_by_id
)

WITH skus AS (
    SELECT
        _active,
        created_at,
        updated_at,
        id,
        handle,
        tags,
        status,
        title,
        images,
        jsonb_array_elements(variants) as v
    FROM
        shopify.shopify_product
)

SELECT
    skus.id as shopify_id,
    (v->>'id')::BIGINT as variant_id,
    v->>'sku' as shopify_sku,
    skus.status,
    (
        CASE
            WHEN title = '' THEN v->>'title' 
            ELSE title
        END || 
        CASE
            WHEN COALESCE((v->>'option1'), 'Default Title') = 'Default Title' THEN ''
            ELSE ' - ' || (v->>'option1')
        END ||
        CASE
            WHEN COALESCE((v->>'option2'), 'Default Title') = 'Default Title' THEN ''
            ELSE ' - ' || (v->>'option2')
        END ||
        CASE
            WHEN COALESCE((v->>'option3'), 'Default Title') = 'Default Title' THEN ''
            ELSE ' - ' || (v->>'option3')
        END
    ) as title,
    v->>'inventory_policy' as inventory_policy,
    COALESCE((v->>'inventory_management'), 'Not Tracked') as inventory_management,
    (v->>'grams')::INTEGER as grams,
    (v->>'price')::NUMERIC(16, 2) as price,
    CASE
        WHEN v->>'inventory_management' IS NOT NULL THEN (v->>'inventory_quantity')::INTEGER
    END as inventory_quantity,
    CASE
        WHEN tags like '%retail-only%' THEN 'Retail'
        WHEN tags like '%wholesale-only%' THEN 'Wholesale'
        ELSE 'All'
    END as customer_type,
    v->>'barcode' as barcode,
    skus.tags,
    skus.handle,
    _active,
    created_at as _created,
    updated_at as _last_updated,
    1 as _created_by_id,
    1 as _last_updated_by_id
FROM
    skus
ON CONFLICT (variant_id)
DO UPDATE
    SET 
        shopify_id = EXCLUDED.shopify_id,
        shopify_sku = EXCLUDED.shopify_sku,
        status = EXCLUDED.status,
        title = EXCLUDED.title,
        inventory_policy = EXCLUDED.inventory_policy,
        inventory_management = EXCLUDED.inventory_management,
        grams = EXCLUDED.grams,
        price = EXCLUDED.price,
        inventory_quantity = EXCLUDED.inventory_quantity,
        customer_type = EXCLUDED.customer_type,
        barcode = EXCLUDED.barcode,
        tags = EXCLUDED.tags,
        handle = EXCLUDED.handle,
        _last_updated = EXCLUDED._last_updated,
        _active = EXCLUDED._active
;
