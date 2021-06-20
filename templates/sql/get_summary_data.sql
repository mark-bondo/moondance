WITH summary AS (
    SELECT
        COALESCE(%(grouping)s, 'None') as name,
        SUM(%(yaxis)s) as y
    FROM
        %(table)s
    WHERE
        0=0 %(filters)s
    GROUP BY
        1
    ORDER BY
        2 DESC NULLS LAST
)

SELECT
    JSON_BUILD_OBJECT(
        'data',
        JSON_BUILD_ARRAY(
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
                'value',
                '%(grouping)s'
            )
        ),
        'options',
        JSON_BUILD_OBJECT(
            'total', 
            SUM(y)
        )
    ) as json_data
FROM
    summary
;
