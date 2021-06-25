WITH data_table AS (
    SELECT
        %(fields)s,
        SUM(%(yaxis)s) as %(yaxis)s
    FROM
        %(table)s
    WHERE
        0=0 %(filters)s
    GROUP BY
        %(fields)s
)

SELECT
    JSON_BUILD_OBJECT(
        'data', JSON_AGG((SELECT row_to_json(_) FROM (SELECT %(fields)s, %(yaxis)s) as _)),
        'options', JSON_BUILD_OBJECT('total', (SELECT sum(%(yaxis)s) FROM data_table))
    ) as json_data
FROM
    data_table
;
