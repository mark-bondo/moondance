WITH line AS (
    SELECT
        %(group)s as name,
        %(xaxis)s as x,
        SUM(%(yaxis)s) as y
    FROM
        report_moondance.sales_orders
    WHERE
        processed_date >= '2020-10-01'
        %(filters)s
    GROUP BY
        1,
        2
    ORDER BY
        1,
        2
)
, detail AS (
    SELECT
        JSON_BUILD_OBJECT(
            'name', name,
            'data', JSON_AGG(
                JSON_BUILD_ARRAY(x, y)
            )
        ) as data
    FROM
        line
    GROUP BY
        name
)

SELECT
    JSON_BUILD_OBJECT(
        'data', JSON_AGG(data),
        'options', JSON_BUILD_OBJECT('total', (SELECT sum(y) FROM line))
    )::TEXT as data
FROM
    detail
;
