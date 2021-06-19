WITH drilldowns AS (
    SELECT
        chart_id,
        JSON_AGG(
            JSONB_BUILD_OBJECT(
                'value', field,
                'text', COALESCE(name, REPLACE(INITCAP(field), '_', ' ')),
                'isVisible', is_visible,
                'isCurrent', is_default,
                'isBreadCrumb', is_default,
                'sortOrder', 0,
                'filter', CASE WHEN filter IS NOT NULL THEN field || filter END
            )
            ORDER BY COALESCE(name, field)
         ) fields
    FROM
        public.automationtools_chart_options
    WHERE
        type = 'grouping' AND
        chart_id = %(id)s
    GROUP BY
        chart_id
    
)

SELECT
    JSONB_BUILD_OBJECT(
        'extraOptions',
        JSONB_BUILD_OBJECT(
            'title', c.title, 
            'prefix', yaxis.yaxis_prefix,
            'drillDowns', drilldowns.fields,
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
    JOIN drilldowns ON c.id = drilldowns.chart_id
WHERE
    c.id = %(id)s
