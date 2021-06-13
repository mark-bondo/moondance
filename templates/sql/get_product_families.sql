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
