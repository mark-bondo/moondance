TRUNCATE TABLE staging.%(table_name)s;
COPY staging.%(table_name)s (%(column_select)s)
FROM STDIN
WITH
    DELIMITER AS '%(delim)s'
    HEADER
    CSV
    QUOTE AS E'\b'
;

INSERT INTO %(schema)s.%(table_name)s (
    sku,
    name,
    attribute,
    product_id,
    status,
    short_description,
    long_description,
    key_words,
    inventory_onhand,
    unit_weight,
    unit_price,
    visibility,
    store_front_link,
    direct_checkout_link,
    datetime_created,
    datetime_updated,
    product_category
)
SELECT
    DISTINCT ON (a.sku)
    a.sku,
    name,
    attribute,
    product_id,
    status,
    short_description,
    long_description,
    key_words,
    inventory.inventory_onhand,
    unit_weight,
    unit_price,
    visibility,
    store_front_link,
    direct_checkout_link,
    datetime_created,
    datetime_updated,
    product_category
FROM
    staging.%(table_name)s a JOIN
    (
        SELECT
            sku,
            SUM(inventory_onhand) as inventory_onhand
        FROM
            staging.%(table_name)s
        GROUP BY
            sku
    ) inventory ON a.sku = inventory.sku
WHERE
    a.sku IS NOT NULL
ORDER BY
    a.sku,
    attribute ASC NULLS LAST,
    datetime_updated DESC
ON CONFLICT (sku)
DO
    UPDATE SET
        name = excluded.name,
        attribute = excluded.attribute,
        product_id = excluded.product_id,
        status = excluded.status,
        short_description = excluded.short_description,
        long_description = excluded.long_description,
        key_words = excluded.key_words,
        inventory_onhand = excluded.inventory_onhand,
        unit_weight = excluded.unit_weight,
        unit_price = excluded.unit_price,
        visibility = excluded.visibility,
        store_front_link = excluded.store_front_link,
        direct_checkout_link = excluded.direct_checkout_link,
        datetime_created = excluded.datetime_created,
        datetime_updated = excluded.datetime_updated,
        product_category = excluded.product_category
;

INSERT INTO public.item_master_nexternal_no_sku(
    %(column_select)s
) 

SELECT
    %(column_select)s
FROM
    staging.%(table_name)s a
WHERE
    a.sku IS NULL
ON CONFLICT ON CONSTRAINT itemmasternexternalnosku_ix1
DO
    UPDATE SET
        product_id = excluded.product_id,
        status = excluded.status,
        short_description = excluded.short_description,
        long_description = excluded.long_description,
        key_words = excluded.key_words,
        inventory_onhand = excluded.inventory_onhand,
        unit_weight = excluded.unit_weight,
        unit_price = excluded.unit_price,
        visibility = excluded.visibility,
        store_front_link = excluded.store_front_link,
        direct_checkout_link = excluded.direct_checkout_link,
        datetime_created = excluded.datetime_created,
        datetime_updated = excluded.datetime_updated,
        product_category = excluded.product_category,
        sku = excluded.sku
;

