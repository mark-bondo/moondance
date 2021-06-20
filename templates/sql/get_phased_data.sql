WITH phased AS (
    SELECT
        COALESCE(%(grouping)s, 'None') as name,
        %(xaxis)s as x,
        SUM(%(yaxis)s) as y
    FROM
        %(table)s
    WHERE
        0=0 %(filters)s
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
        phased
    GROUP BY
        name
)

SELECT
    JSON_BUILD_OBJECT(
        'data', JSON_AGG(data),
        'options', JSON_BUILD_OBJECT('total', (SELECT sum(y) FROM phased))
    ) as json_data
FROM
    detail
;
