WITH pie AS (
    SELECT
        %(grouping)s as name,
        SUM(%(yaxis)s) as y
    FROM
        %(table)s
    WHERE
        processed_date >= '2020-10-01'
        %(filters)s
    GROUP BY
        %(grouping)s
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
        'name',
        INITCAP(REPLACE('%(grouping)s', '_', ' ')),
        'options',
        JSON_BUILD_OBJECT(
            'total', SUM(y)
        )
    )::TEXT as json_data
FROM
    pie
;
