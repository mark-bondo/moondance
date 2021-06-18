SELECT
    JSONB_BUILD_OBJECT(
        'extraOptions',
        JSONB_BUILD_OBJECT(
            'title', c.title, 
            'prefix', yaxis.yaxis_prefix,
            'id', c.id,
            'category', CASE
                            WHEN c.type IN ('pie', 'donut') THEN 'summary'
                            ELSE 'phased'
                        END,
            'sql',
            JSONB_BUILD_OBJECT(
                'table', c.table,
                'grouping', grouping.field,
                'yaxis', yaxis.field,
                'xaxis', xaxis.field,
                'type', c.type,
                'filters', '' -- FIXME
            )
        ),
        'highCharts',
        JSONB_BUILD_OBJECT(
            'chart',
            JSONB_BUILD_OBJECT(
                'type', c.type
            ),
            'legend',
            JSONB_BUILD_OBJECT(
                'enabled', c.show_legend
            ),
            'xAxis',
            JSONB_BUILD_OBJECT(
                'title', xaxis.name,
                'type', xaxis.xaxis_type
            )
        )
    ) as json
FROM
    public.automationtools_chart c
    JOIN public.automationtools_chart_options xaxis ON 
        c.id = xaxis.chart_id AND
        xaxis.is_default = TRUE AND
        xaxis.type = 'xaxis'
    JOIN public.automationtools_chart_options yaxis ON 
        c.id = yaxis.chart_id AND
        yaxis.is_default = TRUE AND
        yaxis.type = 'yaxis'
    JOIN public.automationtools_chart_options grouping ON 
        c.id = grouping.chart_id AND
        grouping.is_default = TRUE AND
        grouping.type = 'grouping' 
WHERE
    c.id = %(id)s
