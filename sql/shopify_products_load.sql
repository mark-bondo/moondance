SELECT DISTINCT ON (
        replace(replace(replace(replace(replace(lower(title), ' ', '-'), '''', ''), '--', '-'), '’', ''), '&', 'and')
    )
    replace(replace(replace(replace(replace(lower(title), ' ', '-'), '''', ''), '--', '-'), '’', ''), '&', 'and') as "Handle",
    title as "Title",
    long_description as "Body (HTML)",
    NULL::TEXT as "Vendor",
    product_category as "Type",
    LOWER(CASE WHEN extra_tags IS NULL THEN '' ELSE extra_tags || ',' END || COALESCE(key_words, '')) as "Tags",
    TRUE as "Published",
    NULL::TEXT as "Option1 Name",
    NULL::TEXT as "Option1 Value",	
    NULL::TEXT as "Option2 Name",
    NULL::TEXT as "Option2 Value",	
    NULL::TEXT as "Option3 Name",
    NULL::TEXT as "Option3 Value",
    sku as "Variant SKU",
    CASE
        WHEN unit_of_measure = 'oz' THEN ROUND(unit_weight::NUMERIC * 453.592::NUMERIC, 0) 
    END as "Variant Grams",
    'shopify' as "Variant Inventory Tracker",
    inventory_onhand as "Variant Inventory Qty",
    'deny' as "Variant Inventory Policy",
    'moondance-soaps' as "Variant Fulfillment Service",
    unit_price as "Variant Price",
    NULL::NUMERIC as "Variant Compare At Price",
    TRUE as "Variant Requires Shipping",
    TRUE as "Variant Taxable",
    NULL::TEXT as "Variant Barcode",
    image_url as "Image Src",
    1 as "Image Position",
    title as "Image Alt Text",
    NULL::TEXT as "Gift Card",
    NULL::TEXT as "SEO Title",
    NULL::TEXT as "SEO Description",
    NULL::TEXT as "Google Shopping / Google Product Category",
    NULL::TEXT as "Google Shopping / Gender",
    NULL::TEXT as "Google Shopping / Age Group",
    NULL::TEXT as "Google Shopping / MPN",
    NULL::TEXT as "Google Shopping / AdWords Grouping",
    NULL::TEXT as "Google Shopping / AdWords Labels",
    NULL::TEXT as "Google Shopping / Condition",
    NULL::TEXT as "Google Shopping / Custom Product",
    NULL::TEXT as "Google Shopping / Custom Label 0",
    NULL::TEXT as "Google Shopping / Custom Label 1",
    NULL::TEXT as "Google Shopping / Custom Label 2",
    NULL::TEXT as "Google Shopping / Custom Label 3",
    NULL::TEXT as "Google Shopping / Custom Label 4",
    NULL::TEXT as "Variant Image",
    unit_of_measure as "Variant Weight Unit",
    NULL::TEXT as "Variant Tax Code",
    NULL::NUMERIC as "Cost per item"
FROM
    "public"."item_master_nexternal"
WHERE
    _active = TRUE
 
    
/*update
    "public"."item_master_nexternal"
set
    shopify_type = product_category
*/