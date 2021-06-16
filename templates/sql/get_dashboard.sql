SELECT
    JSONB_BUILD_OBJECT(
        'id', d.id,
        'charts',
        JSON_AGG(
            JSONB_BUILD_OBJECT(
                'chart',
                JSONB_BUILD_OBJECT(
                    'title', JSONB_BUILD_OBJECT('text', c.title),
                    'type', c.type,
                    'id', c.id
                ),
                'legend',
                JSONB_BUILD_OBJECT(
                    'enabled', c.show_legend
                ),
                'xAxis',
                JSONB_BUILD_OBJECT(
                    'title', xaxis.name,
                    'type', xaxis.xaxis_type,
                    'dateTimeLabelFormats', JSONB_BUILD_OBJECT('month', '%%b %%Y', 'year', '%%Y')
                ),
                'sql',
                JSONB_BUILD_OBJECT(
                    'grouping', grouping.field,
                    'yaxis', yaxis.field,
                    'xaxis', xaxis.field,
                    'filters', '' -- FIXME
                )
            )
        )
    ) as json
FROM
    public.automationtools_dashboard d
    JOIN public.automationtools_dashboard_charts dc ON d.id = dc.dashboard_id
    JOIN public.automationtools_chart c ON dc.chart_id = c.id
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
    d.id = %(id)s
GROUP BY
    d.id
