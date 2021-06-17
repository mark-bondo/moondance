WITH charts AS (
    SELECT
        dashboard_id,
        JSON_AGG(chart_id) as charts
    FROM
        public.automationtools_dashboard_charts
    GROUP BY
        dashboard_id
)

SELECT
    JSON_AGG(
        JSONB_BUILD_OBJECT(
            'id', d.id,
            'name', d.name,
            'type', 'dashboard',
            'charts', charts.charts
        )    
    )::TEXT as json
FROM
    public.automationtools_dashboard d
    JOIN charts ON d.id = charts.dashboard_id
