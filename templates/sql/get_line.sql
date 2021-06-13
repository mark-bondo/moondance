WITH line AS (
    SELECT
        %(group)s as name,
        EXTRACT(epoch FROM %(xaxis)s) as x,
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
    JSON_AGG(data) as data
FROM
    detail
;
