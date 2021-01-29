WITH last_cost AS (
    SELECT
        sku,
        sku_description,
        SUM(total_material_cost)/SUM(quantity_purchased) as unit_material_cost
    FROM
        public.vw_invoice_history
    WHERE
        date_invoiced >= CURRENT_DATE - '6 MONTHS'::INTERVAL
    GROUP BY
        sku,
        sku_description
)

UPDATE
    public.operations_product
SET
    unit_material_cost = last_cost.unit_material_cost
FROM
    last_cost
WHERE
    public.operations_product.sku = last_cost.sku
;