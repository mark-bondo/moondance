WITH recipe AS (
    WITH RECURSIVE exploded_recipe AS (
        SELECT
            parent.sku_parent_id as sku_top_level,
            parent.sku_parent_id as sku_parent,
            parent.sku_id as sku_child,
            parent.unit_of_measure,
            parent.quantity as quantity,
            1 as bom_level
        FROM
            public.operations_recipe_line parent 
        WHERE
            sku_parent_id = %(sku_list)s

        UNION

        SELECT
            boms.sku_top_level,
            child.sku_parent_id as sku_parent,
            child.sku_id as sku_child,
            child.unit_of_measure,
            (child.quantity * boms.quantity)::NUMERIC(12, 5) as quantity,
            boms.bom_level + 1 as bom_level
        FROM
            exploded_recipe boms JOIN
            public.operations_recipe_line child ON child.sku_parent_id = boms.sku_child
    )

    SELECT
        recipe.sku_top_level as product_id,
        parent.description as product_description,
        --wip.id as wip_id,
        wip.description as wip,
        pcode.family,
        child.sku,
        child.description,
        recipe.unit_of_measure,
        recipe.quantity as quantity_needed,
        SUM(recipe.quantity * weight.conversion_rate * child.unit_material_cost)::NUMERIC(16, 2) as material_cost,
        SUM(recipe.quantity * weight.conversion_rate * child.unit_material_cost * (pcode.freight_factor_percentage/100::NUMERIC))::NUMERIC(16, 2) as freight_cost,
        SUM(
            (
                recipe.quantity::NUMERIC * weight.conversion_rate::NUMERIC * 
                (COALESCE(child.unit_material_cost::NUMERIC, 0) + COALESCE(child.unit_labor_cost, 0))
            ) +
            COALESCE(
                recipe.quantity::NUMERIC * weight.conversion_rate::NUMERIC * child.unit_material_cost::NUMERIC * (pcode.freight_factor_percentage::NUMERIC/100::NUMERIC)
            , 0)
        )::NUMERIC as total_cost,
        SUM(COALESCE(inventory.quantity_onhand * weight_inventory.conversion_rate, 0))::NUMERIC(16, 2) as quantity_onhand,
        child.unit_of_measure as purchasing_unit_of_measure,
        (
            child.unit_material_cost::NUMERIC +  
            (child.unit_material_cost::NUMERIC * pcode.freight_factor_percentage::NUMERIC/100::NUMERIC)
        )::NUMERIC(16, 2) as purchasing_cost
    FROM
        exploded_recipe recipe
        JOIN public.operations_product parent ON recipe.sku_top_level = parent.id
        JOIN public.operations_product wip ON recipe.sku_parent = wip.id
        JOIN public.operations_product child ON recipe.sku_child = child.id
        JOIN public.operations_product_code pcode ON child.product_code_id = pcode.id
        JOIN public.operations_weight_conversions weight ON
            child.unit_of_measure = weight.to_measure AND
            recipe.unit_of_measure = weight.from_measure
        LEFT JOIN public.purchasing_inventory_onhand inventory ON child.id = inventory.sku_id 
        JOIN public.operations_weight_conversions weight_inventory ON
            child.unit_of_measure = weight_inventory.from_measure AND
            recipe.unit_of_measure = weight_inventory.to_measure
    WHERE
        pcode.type != 'WIP'
    GROUP BY
        recipe.sku_top_level,
        parent.description,
        --wip.id,
        wip.description,
        pcode.family,
        child.sku,
        child.description,
        recipe.unit_of_measure,
        recipe.quantity,
        child.unit_of_measure,
        (
            child.unit_material_cost::NUMERIC +  
            (child.unit_material_cost::NUMERIC * pcode.freight_factor_percentage::NUMERIC/100::NUMERIC)
        )
    ORDER BY
        child.sku
)

SELECT
    JSONB_AGG(json)
FROM
    (
    SELECT 
        (select row_to_json(_) from (select product_id, wip, product_description, family, sku, description, unit_of_measure, quantity_needed, total_cost, quantity_onhand) as _) as json
    FROM
        recipe
) s
;
