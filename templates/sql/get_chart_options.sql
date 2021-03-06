WITH drilldowns AS (
    SELECT
        chart_id,
        JSON_AGG(
            JSONB_BUILD_OBJECT(
                'value', field,
                'text', COALESCE(name, REPLACE(INITCAP(field), '_', ' ')),
                'isVisible', is_visible,
                'isCurrent', is_default,
                'isBreadCrumb', CASE WHEN "type" = 'grouping' THEN is_default ELSE FALSE END,
                'sort', 0,
                'filter', CASE WHEN filter IS NOT NULL THEN field || filter END,
                'type', "type"
            )
            ORDER BY COALESCE(name, field)
         ) fields
    FROM
        public.automationtools_chart_options
    WHERE
        chart_id = %(id)s
    GROUP BY
        chart_id
    
)

SELECT
    JSONB_BUILD_OBJECT(
        'extraOptions',
        JSONB_BUILD_OBJECT(
            'xAxis', JSONB_BUILD_OBJECT(
                'title', JSONB_BUILD_OBJECT(
                    'field', xaxis.field,
                    'text', COALESCE(xaxis.name, REPLACE(INITCAP(xaxis.field), '_', ' '))
                )
            ),
            'yAxis', JSONB_BUILD_OBJECT(
                'title', JSONB_BUILD_OBJECT(
                    'field', yaxis.field,
                    'text', COALESCE(yaxis.name, REPLACE(INITCAP(yaxis.field), '_', ' '))
                )
            ),
            'title', c.title,
            'prefix', yaxis.yaxis_prefix,
            'fields', drilldowns.fields,
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
            'plotOptions',
            JSONB_BUILD_OBJECT(
                'pie',
                JSONB_BUILD_OBJECT(
                    'minSize', 120,
                    'dataLabels',
                    JSONB_BUILD_OBJECT(
                        'enabled', TRUE,
                        'format', '<b>{point.name}</b><br>' || yaxis.yaxis_prefix || '{point.y:,.0f}'
                    )
                )
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
                    null--COALESCE(xaxis.name, REPLACE(INITCAP(xaxis.field), '_', ' '))
                ),
                'type', xaxis.xaxis_type
            ),
            'yAxis',
            JSONB_BUILD_OBJECT(
                'title', 
                JSONB_BUILD_OBJECT(
                    'text',
                    null --COALESCE(yaxis.name, INITCAP(REPLACE(yaxis.field, '_', ' ')))
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
