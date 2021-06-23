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
                'filter', CASE WHEN filter IS NOT NULL THEN field || filter END,
                'type', 'grouping'
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
            'xAxis',
            xaxis.field,
            'title', c.title, 
            'prefix', yaxis.yaxis_prefix,
            'drillDowns', drilldowns.fields,
            'chartCategory', CASE
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
            'tooltip',
            JSONB_BUILD_OBJECT(
                'valuePrefix', yaxis.yaxis_prefix,
                'valueDecimals', yaxis.yaxis_decimals,
                'pointFormat', CASE
                                    WHEN c.type IN ('pie', 'donut') THEN '{series.name}: <b>{point.y} ({point.percentage:.1f}%%)</b><br/>'
                                    ELSE '{series.name}: <b>{point.y}</b><br/>'
                                END
            ),
            'xAxis',
            JSONB_BUILD_OBJECT(
                'title', 
                JSONB_BUILD_OBJECT(
                    'text',
                    xaxis.name
                ),
                'type', xaxis.xaxis_type
            ),
            'yAxis',
            JSONB_BUILD_OBJECT(
                'title', 
                JSONB_BUILD_OBJECT(
                    'text',
                    COALESCE(yaxis.name, INITCAP(REPLACE(yaxis.field, '_', ' ')))
                )
            ),
            'plotOptions',
            JSONB_BUILD_OBJECT(
                'pie', JSONB_BUILD_OBJECT(
                    'dataLabels', JSONB_BUILD_OBJECT(
                        'enabled', true,
                        'format', '<b>{point.name}</b><br>' || yaxis.yaxis_prefix || '{point.y:,.0f} ({point.percentage:.1f}%%)'
                    )
                )
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
