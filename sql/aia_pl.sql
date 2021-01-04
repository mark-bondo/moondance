drop view aia.vw_order_intake;
create or replace view aia.vw_order_intake as

WITH mtd AS (
    SELECT
        CASE
            WHEN EXTRACT(DOW FROM date_calendar) NOT IN (0,6) THEN TRUE
        END as is_weekday,
        date_calendar,
        fiscal_month_xylem_445,
        fiscal_year_xylem_445
    FROM
        whs.dwhs_fiscaldates
    WHERE
        date_calendar BETWEEN 
            (SELECT start_date FROM public.get_fiscal_date_range(CURRENT_DATE)) AND
            LEAST((SELECT end_date FROM public.get_fiscal_date_range(CURRENT_DATE)), CURRENT_DATE)
)
, pmtd AS (
    SELECT
        CASE
            WHEN EXTRACT(DOW FROM date_calendar) NOT IN (0,6) THEN TRUE
        END as is_weekday,
        date_calendar
    FROM
        whs.dwhs_fiscaldates
    WHERE
        fiscal_year_xylem_445 = (SELECT fiscal_year - 1 FROM public.get_fiscal_dates(CURRENT_DATE)) AND
        fiscal_month_xylem_445 = (SELECT fiscal_month FROM public.get_fiscal_dates(CURRENT_DATE))
    ORDER BY
        is_weekday DESC NULLS LAST,
        date_calendar ASC
    LIMIT (SELECT count(*) FROM mtd WHERE is_weekday = TRUE)
)
, ytd AS (
    SELECT
        CASE
            WHEN EXTRACT(DOW FROM date_calendar) NOT IN (0,6) THEN TRUE
        END as is_weekday,
        date_calendar
    FROM
        whs.dwhs_fiscaldates
    WHERE
        date_calendar <= CURRENT_DATE AND
        fiscal_year_xylem_445 = (SELECT fiscal_year FROM public.get_fiscal_dates(CURRENT_DATE))
)
, pytd AS (
    SELECT
        CASE
            WHEN EXTRACT(DOW FROM date_calendar) NOT IN (0,6) THEN TRUE
        END as is_weekday,
        date_calendar
    FROM
        whs.dwhs_fiscaldates
    WHERE
        fiscal_year_xylem_445 = (SELECT fiscal_year - 1 FROM public.get_fiscal_dates(CURRENT_DATE))
    ORDER BY
        is_weekday DESC NULLS LAST,
        date_calendar ASC
    LIMIT (SELECT count(*) FROM ytd WHERE is_weekday = TRUE)
)
, mtd_days AS (
    SELECT
        count(*) as days
    FROM
        pmtd
    WHERE
        is_weekday = TRUE
)
, pmtd_days AS (
    SELECT
        count(*) as days
    FROM
        mtd
    WHERE
        is_weekday = TRUE
)
, split AS (
    SELECT 
        "id",
        "Account Name",
        "Account ID",
        "Opportunity Name",
        "Opportunity Type",
        "Closed Won date",
        "Amount (converted)",
        "Opportunity Owner",
        "Billing State/Province",
        "Billing Country",
        "Growth Center",
        "Application",
        "Sub-Application",
        "Opportunity ID",
        "Opportunity Reference Number",
        "_created",
        TRIM(UNNEST(STRING_TO_ARRAY("Brand", ';'))) as brand
    FROM
        "salesforce"."vue_sales_orders_closed"
)
, record_count AS (
    SELECT
        "id",
        count(*) as records
    FROM
        split
    GROUP BY
        id
)
, wa AS (
    SELECT 
        split."id",
        "Account Name",
        "Account ID",
        "Opportunity Name",
        "Opportunity Type",
        "Closed Won date",
        ("Amount (converted)" / r.records::NUMERIC)::NUMERIC(16, 2) as "Amount (converted)",
        "Opportunity Owner",
        "Billing State/Province",
        "Billing Country",
        "Growth Center",
        "Application",
        "Sub-Application",
        "Opportunity ID",
        "Opportunity Reference Number",
        "_created",
        brand
    FROM
        split JOIN
        record_count r ON split.id = r.id
    WHERE
        brand IN (
            'EmNet',
            'Valor Water',
            'Visenti',
            'PureAnalytics',
            'Citilogics',
            'Xylem Vue'
        )
)


SELECT
    'Orders' || COALESCE(vue_technologies.technologydescription, 'Unassigned') as lookup,
    COALESCE(vue_technologies.technologydescription, 'Unassigned') as technology,
    brand,
    "Account Name",
    "Account ID",
    "Opportunity Name",
    "Opportunity Type",
    "Closed Won date",
    NULL::DATE as "Fiscal Period Invoiced",
    "Amount (converted)"/1000::NUMERIC as "Amount (converted)",
    "Opportunity Owner",
    "Billing State/Province",
    "Billing Country",
    "Growth Center",
    "Application",
    "Sub-Application",
    "Opportunity ID",
    "Opportunity Reference Number",
    CASE
        WHEN wa."Closed Won date" = CURRENT_DATE THEN "Amount (converted)"
    END/1000::NUMERIC as current_day_sales,
    CASE
        WHEN mtd.date_calendar IS NOT NULL THEN "Amount (converted)" / (SELECT days from mtd_days)
    END/1000::NUMERIC as current_mtd_sales_daily_average,
    CASE
        WHEN pmtd.date_calendar IS NOT NULL THEN "Amount (converted)" / (SELECT days from pmtd_days)
    END/1000::NUMERIC as prior_mtd_sales_daily_average,
    CASE
        WHEN mtd.date_calendar IS NOT NULL THEN "Amount (converted)"
    END/1000::NUMERIC as current_mtd_sales,
    CASE
        WHEN pmtd.date_calendar IS NOT NULL THEN "Amount (converted)"
    END/1000::NUMERIC as prior_mtd_sales,
    CASE
        WHEN ytd.date_calendar IS NOT NULL THEN "Amount (converted)"
    END/1000::NUMERIC as current_ytd_sales,
    CASE
        WHEN pytd.date_calendar IS NOT NULL THEN "Amount (converted)"
    END/1000::NUMERIC as prior_ytd_sales 
FROM
    wa
    LEFT JOIN aia.vue_brands ON wa.brand = vue_brands."BrandDescription"
    LEFT JOIN aia.vue_technologies ON vue_brands."VueTechnologyId" = vue_technologies.technologyid
    LEFT JOIN mtd ON wa."Closed Won date" = mtd.date_calendar
    LEFT JOIN ytd ON wa."Closed Won date" = ytd.date_calendar
    LEFT JOIN pmtd ON wa."Closed Won date" = pmtd.date_calendar
    LEFT JOIN pytd ON wa."Closed Won date" = pytd.date_calendar
WHERE
    wa."Closed Won date" >= (SELECT min(date_calendar) FROM pytd)

UNION ALL

SELECT
    'Sales' || COALESCE(vue_tech.technologydescription, 'Unassigned') as lookup,
    COALESCE(vue_tech.technologydescription, 'Unassigned') as technology,
    NULL::TEXT as brand,
    NULL::TEXT as "Account Name",
    NULL::TEXT as "Account ID",
    NULL::TEXT as "Opportunity Name",
    NULL::TEXT as "Opportunity Type",
    NULL::DATE as "Closed Won date",
    MAKE_DATE(fiscal.fiscal_year_xylem_445, fiscal.fiscal_month_xylem_445, 1) as "Fiscal Period Invoiced",
    -SUM(xa."ExchangeRate" * t."AccountingCurrencyAmount") as "Amount (converted)",
    NULL::TEXT as "Opportunity Owner",
    NULL::TEXT as "Billing State/Province",
    NULL::TEXT as "Billing Country",
    NULL::TEXT as "Growth Center",
    NULL::TEXT as "Application",
    NULL::TEXT as "Sub-Application",
    NULL::TEXT as "Opportunity ID",
    NULL::TEXT as "Opportunity Reference Number",
    -SUM(CASE WHEN t."AccountingDate" = CURRENT_DATE THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END) as current_day_sales,
    -SUM(CASE WHEN mtd.date_calendar IS NOT NULL THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END / (SELECT days::NUMERIC from mtd_days)) as current_mtd_sales_daily_average,
    -SUM(CASE WHEN pmtd.date_calendar IS NOT NULL THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END / (SELECT days::NUMERIC from pmtd_days)) as prior_mtd_sales_daily_average,    
    -SUM(CASE WHEN mtd.date_calendar IS NOT NULL THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END) as current_mtd_sales,
    -SUM(CASE WHEN pmtd.date_calendar IS NOT NULL THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END) as prior_mtd_sales,
    -SUM(CASE WHEN ytd.date_calendar IS NOT NULL THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END) as current_ytd_sales,  
    -SUM(CASE WHEN pytd.date_calendar IS NOT NULL THEN (xa."ExchangeRate" * t."AccountingCurrencyAmount")/1000::NUMERIC END) as prior_ytd_sales  
FROM
    "aia"."general_ledger_transactions" t
    JOIN whs.dwhs_fiscaldates fiscal ON t."AccountingDate" = fiscal.date_calendar
    LEFT JOIN aia.technologies ax_tech ON t."TechnologyId" = ax_tech.technologyid
    LEFT JOIN aia.vue_map_ax_technologies map_tech ON t."TechnologyId" = map_tech.axtechnologyid
    LEFT JOIN aia.vue_technologies vue_tech ON map_tech.vuetechnologyid = vue_tech.technologyid
    LEFT JOIN aia.generalledgeraccounts gl ON t."GLAccountId" = gl.generalledgeraccountid
    LEFT JOIN aia.MonthAverageRatesCompiled xa ON 
        t."AccountingCurrencyCode" = xa."FromCurrencyCode" AND 
        t."AccountingDate" BETWEEN xa."PeriodStartDate" AND xa."PeriodEndDate"
    LEFT JOIN mtd ON t."AccountingDate" = mtd.date_calendar
    LEFT JOIN ytd ON t."AccountingDate" = ytd.date_calendar
    LEFT JOIN pmtd ON t."AccountingDate" = pmtd.date_calendar
    LEFT JOIN pytd ON t."AccountingDate" = pytd.date_calendar
    LEFT JOIN aia.reportingentity r ON
        t."DivisionId" = r.divisionid AND
        t."LegalEntityId" = r.legalentityid AND
        t."TechnologyId" = r.technologyid AND
        t."DepartmentId" = r.departmentid
WHERE
    t."Ledger" <> 'CUSD' and
    gl.generalledgeraccounttype = 'Revenue' AND
    gl.generalledgeraccountcategory <> 'Intercompany Revenue' AND
    fiscal.fiscal_year_xylem_445 >= (SELECT MIN(fiscal_year_xylem_445) - 1 FROM mtd) AND
    t."AccountingDate" <= CURRENT_DATE AND 
    (
        r.AllAIA_09 = 'Digital Solutions'
        OR
        (
            r.DivisionId IS NULL AND 
            t."DivisionId" IN (
                '400', -- EmNet
                '405', -- Aquatune
                '410', -- CitiLogics
                '419', -- Emerging Markets Digital Solutions
                '425', -- Pure Analytics
                '439', -- Europe
                '440', -- Visenti
                '445', -- Confluence
                '460'  -- Valor
            )
        
        )
    )
GROUP BY
    'Sales' || COALESCE(vue_tech.technologydescription, 'Unassigned'),
    COALESCE(vue_tech.technologydescription, 'Unassigned'),
    MAKE_DATE(fiscal.fiscal_year_xylem_445, fiscal.fiscal_month_xylem_445, 1)
;
    
grant usage on schema whs to "Vue Reader";
grant select on aia.vw_order_intake to "Vue Reader";
grant select on whs.dwhs_fiscaldates to "Vue Reader";