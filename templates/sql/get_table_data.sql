WITH data_table AS (
    SELECT
        COALESCE(%(table_fields)s, 'None') as %(table_fields)s,
        SUM(%(yaxis)s) as %(yaxis)s
    FROM
        %(table)s
    WHERE
        0=0 %(filters)s
    GROUP BY
        %(table_fields)s
)

SELECT
    JSON_BUILD_OBJECT(
        'data', JSON_AGG((SELECT row_to_json(_) FROM (SELECT %(table_fields)s, %(yaxis)s) as _) ORDER BY %(yaxis)s DESC NULLS LAST),
        'options', JSON_BUILD_OBJECT('total', (SELECT sum(%(yaxis)s) FROM data_table))
    ) as json_data
FROM
    data_table
;
