SELECT
    JSON_AGG(
        JSONB_BUILD_OBJECT(
            'id', id,
            'name', name
        )    
    )::TEXT as json
FROM
    public.automationtools_dashboard
