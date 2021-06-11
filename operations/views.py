from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
from .models import recalculate_bom_cost


@login_required
def recalculate_cost(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT DISTINCT
                product_id
            FROM
                staging.products
            ;
        """
        cursor.execute(sql)
        products = cursor.fetchall()

    for p in products:
        recalculate_bom_cost(p[0])

    return HttpResponse(products, content_type="application/json")


@login_required
def make_soap(request):
    return render(request, "operations/make-soap.html", context={})


@login_required
def get_product_data(request, family):
    with connection.cursor() as cursor:
        sql = """
            WITH dates AS (
                SELECT 
                    dd::date as month
                FROM generate_series( 
                    '2020-10-01'::DATE
                    , NOW()
                    , '1 month'::interval
                ) dd
            )
            , products AS (
                SELECT
                    sku,
                    description as name,
                    month
                FROM
                    public.operations_product p
                    JOIN public.operations_product_code pcode ON p.product_code_id = pcode.id
                    JOIN dates ON 0=0
                WHERE
                    pcode.family = %(family)s
            )
            , detail AS (
                SELECT
                    products.name,
                    DATE_PART('YEAR', products.month) || '-' || LPAD(DATE_PART('MONTH', products.month)::TEXT, 2, '0') as month,
                    SUM(COALESCE(so.quantity, 0)) as quantity_sold,
                    SUM(COALESCE(so.net_sales, 0)) as total_sales,
                    SUM(COALESCE(so.total_cost, 0)) as total_cost,
                    SUM(COALESCE(so.net_sales, 0) - COALESCE(so.total_cost, 0)) as total_margin
                FROM
                    products 
                    LEFT JOIN report_moondance.sales_orders so ON 
                        products.sku = so.product_sku AND
                        products.month = so.processed_period
                GROUP BY
                    products.name,
                    products.month
                ORDER BY
                    1,2
            )
            , summary AS (
                SELECT
                    name,
                    SUM(quantity_sold) as total_quantity,
                    AVG(quantity_sold) as average_quantity,
                    SUM(total_sales) as total_sales,
                    SUM(total_cost) as total_cost,
                    SUM(total_margin) as total_margin,
                    ARRAY_AGG(month) as xaxis,
                    ARRAY_AGG(quantity_sold) as phased_quantity,
                    ARRAY_AGG(total_sales) as phased_sales,
                    ARRAY_AGG(total_cost) as phased_cost,
                    ARRAY_AGG(total_margin) as phased_margin
                FROM
                    detail
                GROUP BY
                    name
                HAVING
                    SUM(COALESCE(quantity_sold, 0)) <> 0
            )
            SELECT
                JSON_AGG(
                    JSON_BUILD_OBJECT(
                        'name', name,
                        'xaxis', xaxis,
                        'total_quantity', total_quantity,
                        'average_quantity', average_quantity,
                        'total_sales', total_sales,
                        'total_cost', total_cost,
                        'total_margin', total_margin,
                        'phased_quantity', phased_quantity,
                        'phased_sales', phased_sales,
                        'phased_cost', phased_cost,
                        'phased_margin', phased_margin
                    )
                )::TEXT as json
            FROM
                summary
            ;
        """
        cursor.execute(sql, {"family": family})
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data, content_type="application/json")


@login_required
def get_product_families(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT
                JSON_AGG(jsonb_build_object('value', text, 'text', text))::TEXT as json_data
            FROM
                (
                    SELECT DISTINCT
                        family as text
                    FROM
                        public.operations_product_code
                    WHERE
                        type IN ('Finished Goods') AND
                        _active = TRUE
                    ORDER BY
                        family
                ) s
            ;
        """
        cursor.execute(sql)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data, content_type="application/json")


@login_required
def get_products(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT
                JSON_AGG(jsonb_build_object('value', p.id, 'text', p.description || ' (' || p.sku || ')'))::TEXT as json_data
            FROM
                public.operations_product p
                JOIN public.operations_product_code pcode ON p.product_code_id = pcode.id
            WHERE
                pcode.type IN ('Finished Goods', 'WIP', 'Labor Groups') AND
                p._active = TRUE
            ;
        """
        cursor.execute(sql)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data, content_type="application/json")


@login_required
def get_materials(request):
    print(request.GET.getlist("skus[]"), "x" * 50)
    print(request.GET)
    sku_list = [int(x) for x in request.GET.getlist("skus[]")]

    with connection.cursor() as cursor:
        sql = """
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
                        sku_parent_id = ANY(%s)

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
        """
        cursor.execute(sql, [sku_list])
        json_data = cursor.fetchall()[0][0]

    return HttpResponse(json_data, content_type="application/json")
