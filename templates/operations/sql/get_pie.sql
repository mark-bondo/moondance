WITH pie AS (
    SELECT
        %(group)s as name,
        SUM(%(yaxis)s) as y
    FROM
        report_moondance.sales_orders
    WHERE
        processed_date >= '2020-10-01'
        %(filters)s
    GROUP BY
        %(group)s
    ORDER BY
        2 DESC NULLS LAST
)

SELECT
    JSON_BUILD_OBJECT(
        'data',
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'name', name,
                'y', y
            )
        ),
        'options',
        JSON_BUILD_OBJECT(
            'total', SUM(y)
        )
    )::TEXT as json_data
FROM
    pie
;
