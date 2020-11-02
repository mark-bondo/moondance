SELECT DISTINCT ON (replace(replace(lower(name), ' ', '-'), '''', ''))
    replace(replace(lower(name), ' ', '-'), '''', '') as "Handle",
    title as "Title",
    shopify_option_name_1 as "Option1 Name",
    shopify_option_value_1 as "Option1 Value",	
    shopify_option_name_2 as "Option2 Name",
    shopify_option_value_2 as "Option2 Value",	
    NULL::TEXT as "Option3 Name",
    NULL::TEXT as "Option3 Value",
    sku as "SKU",
    NULL::TEXT as "HS Code",
    NULL::TEXT as "COO",
    'not stocked' as "1204 Patterson Road",
    inventory_onhand as "MoonDance Soaps"
FROM
    "public"."item_master_nexternal"
WHERE
    _active = TRUE AND
    inventory_onhand <> 0
 
    
/*update
    "public"."item_master_nexternal"
set
    shopify_type = product_category
*/