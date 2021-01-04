-- View: public.vw_demand_plan_new_analytics_attainment
DROP VIEW public.vw_demand_plan_new_analytics_attainment_view;
DROP VIEW public.vw_demand_plan_analysis;
DROP MATERIALIZED VIEW public.vw_demand_plan_new_analytics_attainment;

CREATE MATERIALIZED VIEW public.vw_demand_plan_new_analytics_attainment
AS
 WITH all_plans AS (
         SELECT vw_demand_plan_new_versions.scenario,
            vw_demand_plan_new_versions.scenario_id,
            vw_demand_plan_new_versions.plan_version,
            vw_demand_plan_new_versions.snapshot_date
           FROM vw_demand_plan_new_versions
        ), accuracy AS (
         SELECT DISTINCT ON (all_plans.snapshot_date) 'Previous Plan '::text AS scenario,
            all_plans.scenario_id,
            all_plans.plan_version,
            all_plans.snapshot_date,
            'Previous Plan '::text AS alias
           FROM all_plans
          WHERE all_plans.snapshot_date >= ((( SELECT max(all_plans_1.snapshot_date) AS max
                   FROM all_plans all_plans_1)) - '1 year 4 mons'::interval) AND all_plans.snapshot_date <= ((( SELECT max(all_plans_1.snapshot_date) AS max
                   FROM all_plans all_plans_1)) - '1 mon'::interval)
          ORDER BY all_plans.snapshot_date DESC, all_plans.scenario_id
        ), plan_versions AS (
        ( SELECT 'Current Forecast'::text AS scenario,
            all_plans.scenario_id,
            all_plans.plan_version,
            all_plans.snapshot_date,
            'Current Forecast'::text AS alias
           FROM all_plans
          WHERE all_plans.scenario_id = 673
         OFFSET 0
         LIMIT 1)
        UNION ALL
        ( SELECT 'Previous Forecast'::text AS scenario,
            all_plans.scenario_id,
            all_plans.plan_version,
            all_plans.snapshot_date,
            'Previous Forecast'::text AS alias
           FROM all_plans
          WHERE all_plans.scenario_id = 673
         OFFSET 1
         LIMIT 1)
        UNION ALL
        ( SELECT 'Budget'::text AS scenario,
            all_plans.scenario_id,
            all_plans.plan_version,
            all_plans.snapshot_date,
            'Budget'::text AS alias
           FROM all_plans
          WHERE all_plans.scenario_id = 1090
         OFFSET 0
         LIMIT 1)
        UNION ALL
        ( SELECT 'Budget'::text AS scenario,
            all_plans.scenario_id,
            all_plans.plan_version,
            all_plans.snapshot_date,
            'Budget - PY'::text AS alias
           FROM all_plans
          WHERE all_plans.scenario_id = 1090
         OFFSET 1
         LIMIT 1)
        UNION ALL
        ( SELECT 'Finance Call'::text AS scenario,
            all_plans.scenario_id,
            all_plans.plan_version,
            all_plans.snapshot_date,
            'Finance Call'::text AS scenario
           FROM all_plans
          WHERE (date_part('MONTH'::text, all_plans.snapshot_date) = ANY (ARRAY[3::double precision, 6::double precision, 9::double precision, 12::double precision])) AND all_plans.snapshot_date < (( SELECT all_plans_1.snapshot_date
                   FROM all_plans all_plans_1
                 OFFSET 0
                 LIMIT 1))
         OFFSET 0
         LIMIT 1)
        UNION ALL
        ( SELECT 'Previous Plan '::text || lpad(row_number() OVER ()::text, 2, '0'::text) AS scenario,
            accuracy.scenario_id,
            accuracy.plan_version,
            accuracy.snapshot_date,
            'Previous Plan '::text || lpad(row_number() OVER ()::text, 2, '0'::text) AS alias
           FROM accuracy
          WHERE accuracy.snapshot_date >= ((( SELECT max(all_plans.snapshot_date) AS max
                   FROM all_plans)) - '1 year 4 mons'::interval) AND accuracy.snapshot_date <= ((( SELECT max(all_plans.snapshot_date) AS max
                   FROM all_plans)) - '1 mon'::interval)
          ORDER BY accuracy.snapshot_date DESC, accuracy.scenario_id DESC)
        ), other_assumptions AS (
        SELECT
        s.planning_name_id,
        '%' || customer_name || '%' as customer_name,
        current_unit_price as unit_sales_price,
        COALESCE(unit_price_override, 0) - COALESCE(current_unit_price, 0) AS unit_price_reduction,
        start_date,
        end_date
    FROM
        public.demand_planning_remediation_pricing r
        JOIN public.demand_planning_salesforce_product_master s ON r.planning_name_id = s.id
        
        
        
        
        ),
        
          as_of_date AS (
         SELECT dwhs_fiscaldates.date_calendar AS as_of_date,
            dwhs_fiscaldates.fiscal_year_xylem_445 AS next_fiscal_year,
            dwhs_fiscaldates.fiscal_month_xylem_445 AS next_fiscal_month,
            dwhs_fiscaldates.fiscal_quarter_label_xylem_445 AS next_fiscal_quarter
           FROM whs.dwhs_fiscaldates
          WHERE dwhs_fiscaldates.date_calendar = ('now'::text::date - '1 day'::interval)::date
        )
        
        
        , plan AS (
         SELECT v.scenario,
            h.snapshot_date,
            h.is_warranty,
            h.order_status_crd,
            h.market,
            h.na_forecast_family,
            h.subfamily,
            h.analytics,
            h.planning_name,
            h.item_number,
            h.item_description,
            h.total_sales::numeric(18,2) AS total_sales,
            h.quantity,
            h.ship_plan_month,
            COALESCE(h.build_plan_month, h.ship_plan_month) AS build_plan_month,
            COALESCE(h.build_plan_quantity, h.quantity) AS build_plan_quantity,
            h.revised_commit_date,
            h.crd_plan_month,
            h.crd_date,
            rollup.name AS consolidated_customer_name,
            h.customer_name_bill_to,
            h.customer_name_ship_to,
            h.project_name,
            h.early_ship,
            h.order_number,
            h.order_line_number,
            h.order_with_line,
            h.unit_sales_price,
            h.unit_standard_material_cost,
            h.unit_material_margin,
            h.total_standard_material_cost::numeric(18,2) AS total_standard_material_cost,
            h.total_material_margin::numeric(18,2) AS total_material_margin,
            h.item_class,
            h.business_unit AS na_business_unit,
            h.crd_year,
            h.ship_year,
            h.ship_quarter,
            h.date_entered,
            h.original_commit_date,
            h.hold_reason,
            h.planner_comments,
            h.salesperson,
            h.crd_quarter,
            h.salesforce_opportunity_name,
            h.planning_name_id,
            h.hyperion_product_name,
            h.source_system,
            h.line_id AS "Line ID",
            h.id,
            h.scenario_id,
            h.plan_revision_number,
            v.plan_version,
            h.project_code,
            h.customer_number_bill_to,
            h.ship_to_number,
            h.consolidated_customer_id,
            h.salesforce_account_id,
            h.salesforce_opportunity_id,
            NULL::date AS date_invoiced,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_sales
                    ELSE NULL::numeric
                END AS total_sales_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_sales
                    ELSE NULL::numeric
                END AS total_sales_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_sales
                    ELSE NULL::numeric
                END AS total_sales_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_standard_material_cost
                    ELSE NULL::numeric
                END AS total_material_cost_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_standard_material_cost
                    ELSE NULL::numeric
                END AS total_material_cost_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_standard_material_cost
                    ELSE NULL::numeric
                END AS total_material_cost_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_tariff_cost
                    ELSE NULL::numeric
                END AS total_tariff_cost_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_tariff_cost
                    ELSE NULL::numeric
                END AS total_tariff_cost_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_tariff_cost
                    ELSE NULL::numeric
                END AS total_tariff_cost_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_freight_cost
                    ELSE NULL::numeric
                END AS total_freight_cost_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_freight_cost
                    ELSE NULL::numeric
                END AS total_freight_cost_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_freight_cost
                    ELSE NULL::numeric
                END AS total_freight_cost_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_base_material_cost
                    ELSE NULL::numeric
                END AS total_base_material_cost_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_base_material_cost
                    ELSE NULL::numeric
                END AS total_base_material_cost_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_base_material_cost
                    ELSE NULL::numeric
                END AS total_base_material_cost_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_cost_tracker_savings
                    ELSE NULL::numeric
                END AS total_cost_tracker_savings_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_cost_tracker_savings
                    ELSE NULL::numeric
                END AS total_cost_tracker_savings_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_cost_tracker_savings
                    ELSE NULL::numeric
                END AS total_cost_tracker_savings_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_vam_savings
                    ELSE NULL::numeric
                END AS total_vam_savings_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_vam_savings
                    ELSE NULL::numeric
                END AS total_vam_savings_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_vam_savings
                    ELSE NULL::numeric
                END AS total_vam_savings_savings_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_cem_surcharges
                    ELSE NULL::numeric
                END AS total_cem_surcharges_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_cem_surcharges
                    ELSE NULL::numeric
                END AS total_cem_surcharges_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_cem_surcharges
                    ELSE NULL::numeric
                END AS total_cem_surcharges_savings_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.total_material_margin
                    ELSE NULL::numeric
                END AS total_material_margin_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.total_material_margin
                    ELSE NULL::numeric
                END AS total_material_margin_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.total_material_margin
                    ELSE NULL::numeric
                END AS total_material_margin_budget,
                CASE
                    WHEN v.scenario = 'Current Forecast'::text THEN h.quantity
                    ELSE NULL::numeric
                END AS total_quantity_current_plan,
                CASE
                    WHEN v.scenario = 'Previous Forecast'::text THEN h.quantity
                    ELSE NULL::numeric
                END AS total_quantity_previous_plan,
                CASE
                    WHEN v.scenario = 'Budget'::text THEN h.quantity
                    ELSE NULL::numeric
                END AS total_quantity_budget,
            h.total_cem_surcharges,
            h.total_vam_savings,
            h.total_base_material_cost,
            h.total_tariff_cost,
            h.total_freight_cost,
            h.total_cost_tracker_savings,
            h.customer_type,
            h.datetime_created,
            pricing.value AS pricing_method,
            costing.value AS costing_method,
            array_to_string(h.cost_tracker_projects_array, '; '::text || '
        '::text) AS cost_tracker_project_list,
            sf.primary_manufacturing_location,
            sf.primary_manufacturing_type,
            NULL::text AS otd_late_reason_summary,
            NULL::text AS otd_late_reason_detail,
            NULL::text AS otp_late_reason_summary,
            NULL::text AS otp_late_reason_detail
           FROM whs.base_demand_plan_history h
             JOIN plan_versions v ON h.plan_version::text = v.plan_version::text
             LEFT JOIN demand_planning_customer_rollup rollup ON h.consolidated_customer_id = rollup.id
             LEFT JOIN datamanager_property_values pricing ON h.pricing_method_id = pricing.id
             LEFT JOIN datamanager_property_values costing ON h.costing_method_id = costing.id
             LEFT JOIN vw_master_salesforce_products sf ON h.planning_name_id::text = sf.planning_name_id::text
          WHERE
                CASE
                    WHEN v.alias = 'Budget - PY'::text AND date_part('YEAR'::text, h.ship_plan_month) = (date_part('YEAR'::text, h.snapshot_date) + 1::double precision) THEN true
                    WHEN v.alias = 'Budget'::text AND date_part('YEAR'::text, h.ship_plan_month) >= (date_part('YEAR'::text, h.snapshot_date) + 1::double precision) THEN true
                    WHEN v.alias <> ALL (ARRAY['Budget'::text, 'Budget - PY'::text]) THEN true
                    ELSE false
                END = true
        ), billings AS (
         SELECT 'Actual'::text AS scenario,
            b.snapshot_date,
            b.is_warranty,
            b.order_status_crd,
            b.market,
            b.na_forecast_family,
            b.subfamily,
            b.analytics,
            b.planning_name,
            b.item_number,
            b.item_description,
            b.total_sales,
            b.quantity,
            b.ship_plan_month,
            b.revised_commit_date,
            b.crd_plan_month,
            b.crd_date,
            b.consolidated_customer_name,
            b.customer_name_bill_to,
            b.customer_name_ship_to,
            b.project_name,
            b.early_ship,
            b.order_number,
            b.order_line_number,
            b.order_with_line,
            b.unit_sales_price,
            b.unit_standard_material_cost,
            b.unit_material_margin,
            b.total_standard_material_cost,
            b.total_material_margin,
            b.item_class,
            b.na_business_unit,
            b.crd_year,
            b.ship_year,
            b.ship_quarter,
            b.date_entered,
            b.original_commit_date,
            b.hold_reason,
            b.planner_comments,
            b.salesperson,
            b.crd_quarter,
            b.salesforce_opportunity_name,
            b.planning_name_id,
            b.hyperion_product_name,
            b.source_system,
            b."Line ID",
            b.id,
            b.scenario_id,
            b.plan_revision_number,
            b.plan_version,
            b.project_code,
            b.customer_number_bill_to,
            b.ship_to_number,
            b.consolidated_customer_id,
            b.salesforce_account_id,
            b.salesforce_opportunity_id,
            b.date_invoiced,
            b.total_sales AS total_sales_current_plan,
            b.total_sales AS total_sales_previous_plan,
            b.total_sales AS total_sales_budget,
            b.total_standard_material_cost AS total_material_cost_current_plan,
            b.total_standard_material_cost AS total_material_cost_previous_plan,
            b.total_standard_material_cost AS total_material_cost_budget,
            NULL::numeric AS total_tariff_cost_current_plan,
            NULL::numeric AS total_tariff_cost_previous_plan,
            NULL::numeric AS total_tariff_cost_budget,
            NULL::numeric AS total_freight_cost_current_plan,
            NULL::numeric AS total_freight_cost_previous_plan,
            NULL::numeric AS total_freight_cost_budget,
            b.total_standard_material_cost AS total_base_material_cost_current_plan,
            b.total_standard_material_cost AS total_base_material_cost_previous_plan,
            b.total_standard_material_cost AS total_base_material_cost_budget,
            NULL::numeric AS total_cost_tracker_savings_current_plan,
            NULL::numeric AS total_cost_tracker_savings_previous_plan,
            NULL::numeric AS total_cost_tracker_savings_budget,
            NULL::numeric AS total_vam_savings_current_plan,
            NULL::numeric AS total_vam_savings_previous_plan,
            NULL::numeric AS total_vam_savings_savings_budget,
            NULL::numeric AS total_cem_surcharges_current_plan,
            NULL::numeric AS total_cem_surcharges_previous_plan,
            NULL::numeric AS total_cem_surcharges_savings_budget,
            b.total_material_margin AS total_material_margin_current_plan,
            b.total_material_margin AS total_material_margin_previous_plan,
            b.total_material_margin AS total_material_margin_budget,
            b.quantity AS total_quantity_current_plan,
            b.quantity AS total_quantity_previous_plan,
            b.quantity AS total_quantity_budget,
            NULL::numeric AS total_cem_surcharges,
            NULL::numeric AS total_vam_savings,
            NULL::numeric AS total_base_material_cost,
            NULL::numeric AS total_tariff_cost,
            NULL::numeric AS total_freight_cost,
            NULL::numeric AS total_cost_tracker_savings,
            b.customer_type,
            NULL::timestamp with time zone AS datetime_created,
            ( SELECT datamanager_property_values.value
                   FROM datamanager_property_values
                  WHERE datamanager_property_values.id = 1095) AS pricing_method,
            ( SELECT datamanager_property_values.value
                   FROM datamanager_property_values
                  WHERE datamanager_property_values.id = 1091) AS costing_method,
            NULL::text AS cost_tracker_project_list,
            sf.primary_manufacturing_location,
            sf.primary_manufacturing_type,
            b.otd_late_reason_summary,
            b.otd_late_reason_detail,
            b.otp_late_reason_summary,
            b.otp_late_reason_detail
           FROM vw_demand_plan_new_billings b
             LEFT JOIN vw_master_salesforce_products sf ON b.planning_name_id::text = sf.planning_name_id::text
          WHERE b.date_invoiced >= (date_trunc('YEAR'::text, 'now'::text::date::timestamp with time zone) - '1 year'::interval) OR b.crd_date >= (date_trunc('YEAR'::text, 'now'::text::date::timestamp with time zone) - '1 year'::interval)
        ), backlog AS (
         SELECT 'Actual'::text AS scenario,
            (b._created - '1 DAYS'::INTERVAL)::DATE as snapshot_date,
            CASE
                WHEN b.unit_sales_price = 0 THEN 'Remediation'
                WHEN b.is_warranty = TRUE THEN 'Warranty'
                ELSE 'Non-Warranty'
            END as is_warranty,

    CASE
        WHEN((date_customer_requested <
                    (
                     SELECT
                            as_of_date.as_of_date
                       FROM
                            as_of_date))
                AND(hold_reason IS NULL)
                AND(date_part('year'::text, date_requested) <>(2030) ::DOUBLE PRECISION))
        THEN 'Backlog - Past Due'::text
        WHEN((date_customer_requested <
                    (
                     SELECT
                            as_of_date.as_of_date
                       FROM
                            as_of_date))
                AND((hold_reason IS NOT NULL)
                    OR(date_part('year'::text, date_requested) =(2030) ::DOUBLE PRECISION)))
        THEN 'On Hold - Past Due'::text
        WHEN((date_customer_requested >=
                    (
                     SELECT
                            as_of_date.as_of_date
                       FROM
                            as_of_date))
                AND((hold_reason IS NOT NULL)
                    OR(date_part('year'::text, date_requested) =(2030) ::DOUBLE PRECISION)))
        THEN 'On Hold - Current'::text
        ELSE 'Backlog - Current'::text
    END AS order_status_crd,
    
            b.market,
            b.na_forecast_family,
            b.subfamily,
            b.analytics,
            b.planning_name,
            b.item_number,
            b.item_description,
            b.total_sales,
            b.quantity,
        CASE
            WHEN b.date_requested <= CURRENT_DATE THEN make_date(( SELECT as_of_date.next_fiscal_year
               FROM as_of_date), ( SELECT as_of_date.next_fiscal_month
               FROM as_of_date), 1)
            ELSE make_date(ship.fiscal_year_xylem_445, ship.fiscal_month_xylem_445, 1)
        END AS ship_plan_month,
            b.date_requested as revised_commit_date,
            MAKE_DATE(crd.fiscal_year_xylem_445, crd.fiscal_month_xylem_445, 1) as crd_plan_month,
            b.date_customer_requested as crd_date,
            b.consolidated_customer_name,
            b.customer_name_bill_to,
            b.customer_name_ship_to,
            b.project_name,
            b.early_ship,
            b.order_number::INTEGER as order_number,
            b.order_line_number::INTEGER as order_line_number,
            b.order_number::TEXT || '-' || b.order_line_number::TEXT as order_with_line,
            b.unit_sales_price,
            b.unit_standard_cost as unit_standard_material_cost,
            COALESCE(b.unit_sales_price, 0) - COALESCE(b.unit_standard_cost, 0) as unit_material_margin,
            b.total_standard_cost as total_standard_material_cost,
            COALESCE(b.total_sales, 0) - COALESCE(b.total_standard_cost, 0) as total_material_margin,
            b.item_class,
            b.na_business_unit,
            crd.fiscal_year_xylem_445 as crd_year,
        CASE
            WHEN b.date_requested <= CURRENT_DATE THEN ( SELECT as_of_date.next_fiscal_year
               FROM as_of_date)
            ELSE ship.fiscal_year_xylem_445
        END AS ship_year,
        CASE
            WHEN b.date_requested <= CURRENT_DATE THEN ( SELECT as_of_date.next_fiscal_quarter
               FROM as_of_date)
            ELSE ship.fiscal_quarter_label_xylem_445
        END AS ship_quarter,
            b.date_entered,
            b.date_committed as original_commit_date,
            b.hold_reason,
            NULL::TEXT as planner_comments,
            b.salesperson,
            crd.fiscal_quarter_label_xylem_445 as crd_quarter,
            NULL::TEXT as salesforce_opportunity_name,
            b.planning_name_id,
            COALESCE(h1.hfm_product_description, h2.hfm_product_description) AS hyperion_product_name,
            'BPCS'::TEXT as source_system,
            NULL::integer AS "Line ID",
            NULL::integer AS id,
            NULL::integer AS scenario_id,
            NULL::integer AS plan_revision_number,
            NULL::text AS plan_version,
            b.project_code,
            b.customer_number_bill_to,
            b.ship_to_number,
            b.consolidated_customer_id,
            NULL::text AS salesforce_account_id,
            NULL::text AS salesforce_opportunity_id,
            NULL::date AS date_invoiced,
            NULL::numeric AS total_sales_current_plan,
            NULL::numeric AS total_sales_previous_plan,
            NULL::numeric AS total_sales_budget,
            NULL::numeric AS total_material_cost_current_plan,
            NULL::numeric AS total_material_cost_previous_plan,
            NULL::numeric AS total_material_cost_budget,
            NULL::numeric AS total_tariff_cost_current_plan,
            NULL::numeric AS total_tariff_cost_previous_plan,
            NULL::numeric AS total_tariff_cost_budget,
            NULL::numeric AS total_freight_cost_current_plan,
            NULL::numeric AS total_freight_cost_previous_plan,
            NULL::numeric AS total_freight_cost_budget,
            NULL::numeric AS total_base_material_cost_current_plan,
            NULL::numeric AS total_base_material_cost_previous_plan,
            NULL::numeric AS total_base_material_cost_budget,
            NULL::numeric AS total_cost_tracker_savings_current_plan,
            NULL::numeric AS total_cost_tracker_savings_previous_plan,
            NULL::numeric AS total_cost_tracker_savings_budget,
            NULL::numeric AS total_vam_savings_current_plan,
            NULL::numeric AS total_vam_savings_previous_plan,
            NULL::numeric AS total_vam_savings_savings_budget,
            NULL::numeric AS total_cem_surcharges_current_plan,
            NULL::numeric AS total_cem_surcharges_previous_plan,
            NULL::numeric AS total_cem_surcharges_savings_budget,
            NULL::numeric AS total_material_margin_current_plan,
            NULL::numeric AS total_material_margin_previous_plan,
            NULL::numeric AS total_material_margin_budget,
            NULL::numeric AS total_quantity_current_plan,
            NULL::numeric AS total_quantity_previous_plan,
            NULL::numeric AS total_quantity_budget,
            NULL::numeric AS total_cem_surcharges,
            NULL::numeric AS total_vam_savings,
            NULL::numeric AS total_base_material_cost,
            NULL::numeric AS total_tariff_cost,
            NULL::numeric AS total_freight_cost,
            NULL::numeric AS total_cost_tracker_savings,
            b.customer_type,
            b._created AS datetime_created,
            ( SELECT datamanager_property_values.value
                   FROM datamanager_property_values
                  WHERE datamanager_property_values.id = 1095) AS pricing_method,
            ( SELECT datamanager_property_values.value
                   FROM datamanager_property_values
                  WHERE datamanager_property_values.id = 1091) AS costing_method,
            NULL::text AS cost_tracker_project_list,
            sf.primary_manufacturing_location,
            sf.primary_manufacturing_type,
            NULL::text AS otd_late_reason_summary,
            NULL::text AS otd_late_reason_detail,
            NULL::text AS otp_late_reason_summary,
            NULL::text AS otp_late_reason_detail
           FROM 
            whs.base_orders b
            LEFT JOIN public.vw_master_salesforce_products sf ON b.planning_name_id::text = sf.planning_name_id::text
            LEFT JOIN whs.dwhs_fiscaldates crd ON b.date_customer_requested = crd.date_calendar
            LEFT JOIN whs.dwhs_fiscaldates ship ON b.date_requested = ship.date_calendar
            LEFT JOIN vw_master_salesperson ssm ON b.salesperson_id = ssm.salesperson_code
            LEFT JOIN whs.hyperion_product_planning_name_map h1 ON b.planning_name_id::text = h1.planning_name_id::text AND h1.na_business_unit::text = ssm.business_unit_name::text
            LEFT JOIN whs.hyperion_product_planning_name_map h2 ON b.planning_name_id::text = h2.planning_name_id::text AND h1.planning_name_id IS NULL AND h2.na_business_unit IS NULL
             WHERE order_status <> 'Billed'
        ), combined AS (
         SELECT billings.scenario,
            billings.snapshot_date,
            billings.is_warranty,
            billings.order_status_crd,
            billings.market,
            billings.na_forecast_family,
            billings.subfamily,
            billings.analytics,
            billings.planning_name,
            billings.item_number,
            billings.item_description,
            billings.total_sales,
            billings.quantity,
            billings.ship_plan_month,
            billings.revised_commit_date,
            billings.crd_plan_month,
            billings.crd_date,
            billings.consolidated_customer_name,
            billings.customer_name_bill_to,
            billings.customer_name_ship_to,
            billings.project_name,
            billings.early_ship,
            billings.order_number,
            billings.order_line_number,
            billings.order_with_line,
            billings.unit_sales_price,
            billings.unit_standard_material_cost,
            billings.unit_material_margin,
            billings.total_standard_material_cost,
            billings.total_material_margin,
            billings.item_class,
            billings.na_business_unit,
            billings.crd_year,
            billings.ship_year,
            billings.ship_quarter,
            billings.date_entered,
            billings.original_commit_date,
            billings.hold_reason,
            billings.planner_comments,
            billings.salesperson,
            billings.crd_quarter,
            billings.salesforce_opportunity_name,
            billings.planning_name_id,
            billings.hyperion_product_name,
            billings.source_system,
            billings."Line ID",
            billings.id,
            billings.scenario_id,
            billings.plan_revision_number,
            billings.plan_version,
            billings.project_code,
            billings.customer_number_bill_to,
            billings.ship_to_number,
            billings.consolidated_customer_id,
            billings.salesforce_account_id,
            billings.salesforce_opportunity_id,
            billings.date_invoiced,
            billings.total_sales_current_plan,
            billings.total_sales_previous_plan,
            billings.total_sales_budget,
            billings.total_material_cost_current_plan,
            billings.total_material_cost_previous_plan,
            billings.total_material_cost_budget,
            billings.total_tariff_cost_current_plan,
            billings.total_tariff_cost_previous_plan,
            billings.total_tariff_cost_budget,
            billings.total_freight_cost_current_plan,
            billings.total_freight_cost_previous_plan,
            billings.total_freight_cost_budget,
            billings.total_base_material_cost_current_plan,
            billings.total_base_material_cost_previous_plan,
            billings.total_base_material_cost_budget,
            billings.total_cost_tracker_savings_current_plan,
            billings.total_cost_tracker_savings_previous_plan,
            billings.total_cost_tracker_savings_budget,
            billings.total_vam_savings_current_plan,
            billings.total_vam_savings_previous_plan,
            billings.total_vam_savings_savings_budget,
            billings.total_cem_surcharges_current_plan,
            billings.total_cem_surcharges_previous_plan,
            billings.total_cem_surcharges_savings_budget,
            billings.total_material_margin_current_plan,
            billings.total_material_margin_previous_plan,
            billings.total_material_margin_budget,
            billings.total_quantity_current_plan,
            billings.total_quantity_previous_plan,
            billings.total_quantity_budget,
            billings.total_cem_surcharges,
            billings.total_vam_savings,
            billings.total_base_material_cost,
            billings.total_tariff_cost,
            billings.total_freight_cost,
            billings.total_cost_tracker_savings,
            billings.customer_type,
            billings.datetime_created,
            billings.pricing_method,
            billings.costing_method,
            billings.cost_tracker_project_list,
            billings.primary_manufacturing_location,
            billings.primary_manufacturing_type,
            billings.otd_late_reason_summary,
            billings.otd_late_reason_detail,
            billings.otp_late_reason_summary,
            billings.otp_late_reason_detail
           FROM billings
        UNION ALL
         SELECT backlog.scenario,
            backlog.snapshot_date,
            backlog.is_warranty,
            backlog.order_status_crd,
            backlog.market,
            backlog.na_forecast_family,
            backlog.subfamily,
            backlog.analytics,
            backlog.planning_name,
            backlog.item_number,
            backlog.item_description,
            backlog.total_sales,
            backlog.quantity,
            backlog.ship_plan_month,
            backlog.revised_commit_date,
            backlog.crd_plan_month,
            backlog.crd_date,
            backlog.consolidated_customer_name,
            backlog.customer_name_bill_to,
            backlog.customer_name_ship_to,
            backlog.project_name,
            backlog.early_ship,
            backlog.order_number,
            backlog.order_line_number,
            backlog.order_with_line,
            backlog.unit_sales_price,
            backlog.unit_standard_material_cost,
            backlog.unit_material_margin,
            backlog.total_standard_material_cost,
            backlog.total_material_margin,
            backlog.item_class,
            backlog.na_business_unit,
            backlog.crd_year,
            backlog.ship_year,
            backlog.ship_quarter,
            backlog.date_entered,
            backlog.original_commit_date,
            backlog.hold_reason,
            backlog.planner_comments,
            backlog.salesperson,
            backlog.crd_quarter,
            backlog.salesforce_opportunity_name,
            backlog.planning_name_id,
            backlog.hyperion_product_name,
            backlog.source_system,
            backlog."Line ID",
            backlog.id,
            backlog.scenario_id,
            backlog.plan_revision_number,
            backlog.plan_version,
            backlog.project_code,
            backlog.customer_number_bill_to,
            backlog.ship_to_number,
            backlog.consolidated_customer_id,
            backlog.salesforce_account_id,
            backlog.salesforce_opportunity_id,
            backlog.date_invoiced,
            backlog.total_sales_current_plan,
            backlog.total_sales_previous_plan,
            backlog.total_sales_budget,
            backlog.total_material_cost_current_plan,
            backlog.total_material_cost_previous_plan,
            backlog.total_material_cost_budget,
            backlog.total_tariff_cost_current_plan,
            backlog.total_tariff_cost_previous_plan,
            backlog.total_tariff_cost_budget,
            backlog.total_freight_cost_current_plan,
            backlog.total_freight_cost_previous_plan,
            backlog.total_freight_cost_budget,
            backlog.total_base_material_cost_current_plan,
            backlog.total_base_material_cost_previous_plan,
            backlog.total_base_material_cost_budget,
            backlog.total_cost_tracker_savings_current_plan,
            backlog.total_cost_tracker_savings_previous_plan,
            backlog.total_cost_tracker_savings_budget,
            backlog.total_vam_savings_current_plan,
            backlog.total_vam_savings_previous_plan,
            backlog.total_vam_savings_savings_budget,
            backlog.total_cem_surcharges_current_plan,
            backlog.total_cem_surcharges_previous_plan,
            backlog.total_cem_surcharges_savings_budget,
            backlog.total_material_margin_current_plan,
            backlog.total_material_margin_previous_plan,
            backlog.total_material_margin_budget,
            backlog.total_quantity_current_plan,
            backlog.total_quantity_previous_plan,
            backlog.total_quantity_budget,
            backlog.total_cem_surcharges,
            backlog.total_vam_savings,
            backlog.total_base_material_cost,
            backlog.total_tariff_cost,
            backlog.total_freight_cost,
            backlog.total_cost_tracker_savings,
            backlog.customer_type,
            backlog.datetime_created,
            backlog.pricing_method,
            backlog.costing_method,
            backlog.cost_tracker_project_list,
            backlog.primary_manufacturing_location,
            backlog.primary_manufacturing_type,
            backlog.otd_late_reason_summary,
            backlog.otd_late_reason_detail,
            backlog.otp_late_reason_summary,
            backlog.otp_late_reason_detail
           FROM backlog
        ), assumptions AS (
         SELECT 'Actual'::text AS scenario,
            b.snapshot_date,
            b.is_warranty,
            b.order_status_crd,
            b.market,
            b.na_forecast_family,
            b.subfamily,
            b.analytics,
            b.planning_name,
            b.item_number,
            b.item_description,
            (b.quantity * other_planning_name.unit_price_reduction::numeric(16,2))::numeric(16,2) AS total_sales,
            NULL::integer AS quantity,
            b.ship_plan_month,
            b.revised_commit_date,
            b.crd_plan_month,
            b.crd_date,
            b.consolidated_customer_name,
            b.customer_name_bill_to,
            b.customer_name_ship_to,
            b.project_name,
            b.early_ship,
            b.order_number,
            b.order_line_number,
            b.order_with_line,
            other_planning_name.unit_price_reduction::numeric(16,2) AS unit_sales_price,
            NULL::numeric(16,2) AS unit_standard_cost,
            other_planning_name.unit_price_reduction::numeric(16,2) AS unit_material_margin,
            NULL::numeric(16,2) AS total_standard_material_cost,
            (b.quantity * other_planning_name.unit_price_reduction)::numeric(16,2) AS total_material_margin,
            b.item_class,
            b.na_business_unit,
            b.crd_year,
            b.ship_year,
            b.ship_quarter,
            b.date_entered,
            b.original_commit_date,
            b.hold_reason,
            b.planner_comments,
            b.salesperson,
            b.crd_quarter,
            b.salesforce_opportunity_name,
            b.planning_name_id,
            b.hyperion_product_name,
            'Sensei'::text AS source_system,
            b."Line ID",
            b.id,
            b.scenario_id,
            b.plan_revision_number,
            b.plan_version,
            b.project_code,
            b.customer_number_bill_to,
            b.ship_to_number,
            b.consolidated_customer_id,
            b.salesforce_account_id,
            b.salesforce_opportunity_id,
            b.date_invoiced,
            (b.quantity * other_planning_name.unit_price_reduction)::numeric(16,2) AS total_sales_current_plan,
            (b.quantity * other_planning_name.unit_price_reduction)::numeric(16,2) AS total_sales_previous_plan,
            (b.quantity *  other_planning_name.unit_price_reduction)::numeric(16,2) AS total_sales_budget,
            NULL::numeric(16,2) AS total_material_cost_current_plan,
            NULL::numeric(16,2) AS total_material_cost_previous_plan,
            NULL::numeric(16,2) AS total_material_cost_budget,
            NULL::numeric(16,2) AS total_tariff_cost_current_plan,
            NULL::numeric(16,2) AS total_tariff_cost_previous_plan,
            NULL::numeric(16,2) AS total_tariff_cost_budget,
            NULL::numeric AS total_freight_cost_current_plan,
            NULL::numeric AS total_freight_cost_previous_plan,
            NULL::numeric AS total_freight_cost_budget,
            NULL::numeric(16,2) AS total_base_material_cost_current_plan,
            NULL::numeric(16,2) AS total_base_material_cost_previous_plan,
            NULL::numeric(16,2) AS total_base_material_cost_budget,
            NULL::numeric AS total_cost_tracker_savings_current_plan,
            NULL::numeric AS total_cost_tracker_savings_previous_plan,
            NULL::numeric AS total_cost_tracker_savings_budget,
            NULL::numeric AS total_vam_savings_current_plan,
            NULL::numeric AS total_vam_savings_previous_plan,
            NULL::numeric AS total_vam_savings_savings_budget,
            NULL::numeric AS total_cem_surcharges_current_plan,
            NULL::numeric AS total_cem_surcharges_previous_plan,
            NULL::numeric AS total_cem_surcharges_savings_budget,
            (b.quantity  *  other_planning_name.unit_price_reduction)::numeric(16,2) AS total_material_margin_current_plan,
            (b.quantity  *  other_planning_name.unit_price_reduction)::numeric(16,2) AS total_material_margin_previous_plan,
            (b.quantity  *  other_planning_name.unit_price_reduction)::numeric(16,2) AS total_material_margin_budget,
            NULL::numeric(16,2) AS total_quantity_current_plan,
            NULL::numeric(16,2) AS total_quantity_previous_plan,
            NULL::numeric(16,2) AS total_quantity_budget,
            NULL::numeric AS total_cem_surcharges,
            NULL::numeric AS total_vam_savings,
            NULL::numeric AS total_base_material_cost,
            NULL::numeric AS total_tariff_cost,
            NULL::numeric AS total_freight_cost,
            NULL::numeric AS total_cost_tracker_savings,
            b.customer_type,
            b.datetime_created,
            ( SELECT datamanager_property_values.value
                   FROM datamanager_property_values
                  WHERE datamanager_property_values.id = 1095) AS pricing_method,
            ( SELECT datamanager_property_values.value
                   FROM datamanager_property_values
                  WHERE datamanager_property_values.id = 1091) AS costing_method,
            NULL::text AS cost_tracker_project_list,
            sf.primary_manufacturing_location,
            sf.primary_manufacturing_type,
            b.otd_late_reason_summary,
            b.otd_late_reason_detail,
            b.otp_late_reason_summary,
            b.otp_late_reason_detail
           FROM combined b
             LEFT JOIN vw_master_salesforce_products sf ON b.planning_name_id::text = sf.planning_name_id::text
    JOIN other_assumptions other_planning_name ON
        b.planning_name_id = other_planning_name.planning_name_id AND
        b.unit_sales_price = other_planning_name.unit_sales_price AND
        b.ship_plan_month BETWEEN other_planning_name.start_date AND other_planning_name.end_date AND
        (
            b.customer_name_bill_to ILIKE other_planning_name.customer_name
            OR
            b.customer_name_ship_to ILIKE other_planning_name.customer_name
            OR
            b.project_name ILIKE other_planning_name.customer_name
        )
        )
 SELECT plan.scenario,
    plan.snapshot_date,
    plan.is_warranty,
    plan.order_status_crd,
    plan.market,
    plan.na_forecast_family,
    plan.subfamily,
    plan.analytics,
    plan.planning_name,
    plan.item_number,
    plan.item_description,
    plan.total_sales,
    plan.quantity,
    plan.ship_plan_month,
    plan.build_plan_month,
    plan.build_plan_quantity,
    plan.revised_commit_date,
    plan.crd_plan_month,
    plan.crd_date,
    plan.consolidated_customer_name,
    plan.customer_name_bill_to,
    plan.customer_name_ship_to,
    plan.project_name,
    plan.early_ship,
    plan.order_number,
    plan.order_line_number,
    plan.order_with_line,
    plan.unit_sales_price,
    plan.unit_standard_material_cost,
    plan.unit_material_margin,
    plan.total_standard_material_cost,
    plan.total_material_margin,
    plan.item_class,
    plan.na_business_unit,
    plan.crd_year,
    plan.ship_year,
    plan.ship_quarter,
    plan.date_entered,
    plan.original_commit_date,
    plan.hold_reason,
    plan.planner_comments,
    plan.salesperson,
    plan.crd_quarter,
    plan.salesforce_opportunity_name,
    plan.planning_name_id,
    plan.hyperion_product_name,
    plan.source_system,
    plan."Line ID",
    plan.id,
    plan.scenario_id,
    plan.plan_revision_number,
    plan.plan_version,
    plan.project_code,
    plan.customer_number_bill_to,
    plan.ship_to_number,
    plan.consolidated_customer_id,
    plan.salesforce_account_id,
    plan.salesforce_opportunity_id,
    plan.date_invoiced,
    plan.total_sales_current_plan,
    plan.total_sales_previous_plan,
    plan.total_sales_budget,
    plan.total_material_cost_current_plan,
    plan.total_material_cost_previous_plan,
    plan.total_material_cost_budget,
    plan.total_tariff_cost_current_plan,
    plan.total_tariff_cost_previous_plan,
    plan.total_tariff_cost_budget,
    plan.total_freight_cost_current_plan,
    plan.total_freight_cost_previous_plan,
    plan.total_freight_cost_budget,
    plan.total_base_material_cost_current_plan,
    plan.total_base_material_cost_previous_plan,
    plan.total_base_material_cost_budget,
    plan.total_cost_tracker_savings_current_plan,
    plan.total_cost_tracker_savings_previous_plan,
    plan.total_cost_tracker_savings_budget,
    plan.total_vam_savings_current_plan,
    plan.total_vam_savings_previous_plan,
    plan.total_vam_savings_savings_budget,
    plan.total_cem_surcharges_current_plan,
    plan.total_cem_surcharges_previous_plan,
    plan.total_cem_surcharges_savings_budget,
    plan.total_material_margin_current_plan,
    plan.total_material_margin_previous_plan,
    plan.total_material_margin_budget,
    plan.total_quantity_current_plan,
    plan.total_quantity_previous_plan,
    plan.total_quantity_budget,
    plan.total_cem_surcharges,
    plan.total_vam_savings,
    plan.total_base_material_cost,
    plan.total_tariff_cost,
    plan.total_freight_cost,
    plan.total_cost_tracker_savings,
    plan.customer_type,
    plan.datetime_created,
    plan.pricing_method,
    plan.costing_method,
    plan.cost_tracker_project_list,
    plan.primary_manufacturing_location,
    plan.primary_manufacturing_type,
    plan.otd_late_reason_summary,
    plan.otd_late_reason_detail,
    plan.otp_late_reason_summary,
    plan.otp_late_reason_detail
   FROM plan
UNION ALL
 SELECT billings.scenario,
    billings.snapshot_date,
    billings.is_warranty,
    billings.order_status_crd,
    billings.market,
    billings.na_forecast_family,
    billings.subfamily,
    billings.analytics,
    billings.planning_name,
    billings.item_number,
    billings.item_description,
    billings.total_sales,
    billings.quantity,
    billings.ship_plan_month,
    NULL::date AS build_plan_month,
    NULL::numeric AS build_plan_quantity,
    billings.revised_commit_date,
    billings.crd_plan_month,
    billings.crd_date,
    billings.consolidated_customer_name,
    billings.customer_name_bill_to,
    billings.customer_name_ship_to,
    billings.project_name,
    billings.early_ship,
    billings.order_number,
    billings.order_line_number,
    billings.order_with_line,
    billings.unit_sales_price,
    billings.unit_standard_material_cost,
    billings.unit_material_margin,
    billings.total_standard_material_cost,
    billings.total_material_margin,
    billings.item_class,
    billings.na_business_unit,
    billings.crd_year,
    billings.ship_year,
    billings.ship_quarter,
    billings.date_entered,
    billings.original_commit_date,
    billings.hold_reason,
    billings.planner_comments,
    billings.salesperson,
    billings.crd_quarter,
    billings.salesforce_opportunity_name,
    billings.planning_name_id,
    billings.hyperion_product_name,
    billings.source_system,
    billings."Line ID",
    billings.id,
    billings.scenario_id,
    billings.plan_revision_number,
    billings.plan_version,
    billings.project_code,
    billings.customer_number_bill_to,
    billings.ship_to_number,
    billings.consolidated_customer_id,
    billings.salesforce_account_id,
    billings.salesforce_opportunity_id,
    billings.date_invoiced,
    billings.total_sales_current_plan,
    billings.total_sales_previous_plan,
    billings.total_sales_budget,
    billings.total_material_cost_current_plan,
    billings.total_material_cost_previous_plan,
    billings.total_material_cost_budget,
    billings.total_tariff_cost_current_plan,
    billings.total_tariff_cost_previous_plan,
    billings.total_tariff_cost_budget,
    billings.total_freight_cost_current_plan,
    billings.total_freight_cost_previous_plan,
    billings.total_freight_cost_budget,
    billings.total_base_material_cost_current_plan,
    billings.total_base_material_cost_previous_plan,
    billings.total_base_material_cost_budget,
    billings.total_cost_tracker_savings_current_plan,
    billings.total_cost_tracker_savings_previous_plan,
    billings.total_cost_tracker_savings_budget,
    billings.total_vam_savings_current_plan,
    billings.total_vam_savings_previous_plan,
    billings.total_vam_savings_savings_budget,
    billings.total_cem_surcharges_current_plan,
    billings.total_cem_surcharges_previous_plan,
    billings.total_cem_surcharges_savings_budget,
    billings.total_material_margin_current_plan,
    billings.total_material_margin_previous_plan,
    billings.total_material_margin_budget,
    billings.total_quantity_current_plan,
    billings.total_quantity_previous_plan,
    billings.total_quantity_budget,
    billings.total_cem_surcharges,
    billings.total_vam_savings,
    billings.total_base_material_cost,
    billings.total_tariff_cost,
    billings.total_freight_cost,
    billings.total_cost_tracker_savings,
    billings.customer_type,
    billings.datetime_created,
    billings.pricing_method,
    billings.costing_method,
    billings.cost_tracker_project_list,
    billings.primary_manufacturing_location,
    billings.primary_manufacturing_type,
    billings.otd_late_reason_summary,
    billings.otd_late_reason_detail,
    billings.otp_late_reason_summary,
    billings.otp_late_reason_detail
   FROM billings
UNION ALL
 SELECT backlog.scenario,
    backlog.snapshot_date,
    backlog.is_warranty,
    backlog.order_status_crd,
    backlog.market,
    backlog.na_forecast_family,
    backlog.subfamily,
    backlog.analytics,
    backlog.planning_name,
    backlog.item_number,
    backlog.item_description,
    backlog.total_sales,
    backlog.quantity,
    backlog.ship_plan_month,
    NULL::date AS build_plan_month,
    NULL::numeric AS build_plan_quantity,
    backlog.revised_commit_date,
    backlog.crd_plan_month,
    backlog.crd_date,
    backlog.consolidated_customer_name,
    backlog.customer_name_bill_to,
    backlog.customer_name_ship_to,
    backlog.project_name,
    backlog.early_ship,
    backlog.order_number,
    backlog.order_line_number,
    backlog.order_with_line,
    backlog.unit_sales_price,
    backlog.unit_standard_material_cost,
    backlog.unit_material_margin,
    backlog.total_standard_material_cost,
    backlog.total_material_margin,
    backlog.item_class,
    backlog.na_business_unit,
    backlog.crd_year,
    backlog.ship_year,
    backlog.ship_quarter,
    backlog.date_entered,
    backlog.original_commit_date,
    backlog.hold_reason,
    backlog.planner_comments,
    backlog.salesperson,
    backlog.crd_quarter,
    backlog.salesforce_opportunity_name,
    backlog.planning_name_id,
    backlog.hyperion_product_name,
    backlog.source_system,
    backlog."Line ID",
    backlog.id,
    backlog.scenario_id,
    backlog.plan_revision_number,
    backlog.plan_version,
    backlog.project_code,
    backlog.customer_number_bill_to,
    backlog.ship_to_number,
    backlog.consolidated_customer_id,
    backlog.salesforce_account_id,
    backlog.salesforce_opportunity_id,
    backlog.date_invoiced,
    backlog.total_sales_current_plan,
    backlog.total_sales_previous_plan,
    backlog.total_sales_budget,
    backlog.total_material_cost_current_plan,
    backlog.total_material_cost_previous_plan,
    backlog.total_material_cost_budget,
    backlog.total_tariff_cost_current_plan,
    backlog.total_tariff_cost_previous_plan,
    backlog.total_tariff_cost_budget,
    backlog.total_freight_cost_current_plan,
    backlog.total_freight_cost_previous_plan,
    backlog.total_freight_cost_budget,
    backlog.total_base_material_cost_current_plan,
    backlog.total_base_material_cost_previous_plan,
    backlog.total_base_material_cost_budget,
    backlog.total_cost_tracker_savings_current_plan,
    backlog.total_cost_tracker_savings_previous_plan,
    backlog.total_cost_tracker_savings_budget,
    backlog.total_vam_savings_current_plan,
    backlog.total_vam_savings_previous_plan,
    backlog.total_vam_savings_savings_budget,
    backlog.total_cem_surcharges_current_plan,
    backlog.total_cem_surcharges_previous_plan,
    backlog.total_cem_surcharges_savings_budget,
    backlog.total_material_margin_current_plan,
    backlog.total_material_margin_previous_plan,
    backlog.total_material_margin_budget,
    backlog.total_quantity_current_plan,
    backlog.total_quantity_previous_plan,
    backlog.total_quantity_budget,
    backlog.total_cem_surcharges,
    backlog.total_vam_savings,
    backlog.total_base_material_cost,
    backlog.total_tariff_cost,
    backlog.total_freight_cost,
    backlog.total_cost_tracker_savings,
    backlog.customer_type,
    backlog.datetime_created,
    backlog.pricing_method,
    backlog.costing_method,
    backlog.cost_tracker_project_list,
    backlog.primary_manufacturing_location,
    backlog.primary_manufacturing_type,
    backlog.otd_late_reason_summary,
    backlog.otd_late_reason_detail,
    backlog.otp_late_reason_summary,
    backlog.otp_late_reason_detail
   FROM backlog
UNION ALL
 SELECT assumptions.scenario,
    assumptions.snapshot_date,
    assumptions.is_warranty,
    assumptions.order_status_crd,
    assumptions.market,
    assumptions.na_forecast_family,
    assumptions.subfamily,
    assumptions.analytics,
    assumptions.planning_name,
    assumptions.item_number,
    assumptions.item_description,
    assumptions.total_sales,
    assumptions.quantity,
    assumptions.ship_plan_month,
    NULL::date AS build_plan_month,
    NULL::numeric AS build_plan_quantity,
    assumptions.revised_commit_date,
    assumptions.crd_plan_month,
    assumptions.crd_date,
    assumptions.consolidated_customer_name,
    assumptions.customer_name_bill_to,
    assumptions.customer_name_ship_to,
    assumptions.project_name,
    assumptions.early_ship,
    assumptions.order_number,
    assumptions.order_line_number,
    assumptions.order_with_line,
    assumptions.unit_sales_price,
    assumptions.unit_standard_cost AS unit_standard_material_cost,
    assumptions.unit_material_margin,
    assumptions.total_standard_material_cost,
    assumptions.total_material_margin,
    assumptions.item_class,
    assumptions.na_business_unit,
    assumptions.crd_year,
    assumptions.ship_year,
    assumptions.ship_quarter,
    assumptions.date_entered,
    assumptions.original_commit_date,
    assumptions.hold_reason,
    assumptions.planner_comments,
    assumptions.salesperson,
    assumptions.crd_quarter,
    assumptions.salesforce_opportunity_name,
    assumptions.planning_name_id,
    assumptions.hyperion_product_name,
    assumptions.source_system,
    assumptions."Line ID",
    assumptions.id,
    assumptions.scenario_id,
    assumptions.plan_revision_number,
    assumptions.plan_version,
    assumptions.project_code,
    assumptions.customer_number_bill_to,
    assumptions.ship_to_number,
    assumptions.consolidated_customer_id,
    assumptions.salesforce_account_id,
    assumptions.salesforce_opportunity_id,
    assumptions.date_invoiced,
    assumptions.total_sales_current_plan,
    assumptions.total_sales_previous_plan,
    assumptions.total_sales_budget,
    assumptions.total_material_cost_current_plan,
    assumptions.total_material_cost_previous_plan,
    assumptions.total_material_cost_budget,
    assumptions.total_freight_cost_current_plan AS total_tariff_cost_current_plan,
    assumptions.total_freight_cost_previous_plan AS total_tariff_cost_previous_plan,
    assumptions.total_freight_cost_budget AS total_tariff_cost_budget,
    assumptions.total_tariff_cost_current_plan AS total_freight_cost_current_plan,
    assumptions.total_tariff_cost_previous_plan AS total_freight_cost_previous_plan,
    assumptions.total_tariff_cost_budget AS total_freight_cost_budget,
    assumptions.total_base_material_cost_current_plan,
    assumptions.total_base_material_cost_previous_plan,
    assumptions.total_base_material_cost_budget,
    assumptions.total_cost_tracker_savings_current_plan,
    assumptions.total_cost_tracker_savings_previous_plan,
    assumptions.total_cost_tracker_savings_budget,
    assumptions.total_vam_savings_current_plan,
    assumptions.total_vam_savings_previous_plan,
    assumptions.total_vam_savings_savings_budget,
    assumptions.total_cem_surcharges_current_plan,
    assumptions.total_cem_surcharges_previous_plan,
    assumptions.total_cem_surcharges_savings_budget,
    assumptions.total_material_margin_current_plan,
    assumptions.total_material_margin_previous_plan,
    assumptions.total_material_margin_budget,
    assumptions.total_quantity_current_plan,
    assumptions.total_quantity_previous_plan,
    assumptions.total_quantity_budget,
    assumptions.total_cem_surcharges,
    assumptions.total_vam_savings,
    assumptions.total_base_material_cost,
    assumptions.total_tariff_cost,
    assumptions.total_freight_cost,
    assumptions.total_cost_tracker_savings,
    assumptions.customer_type,
    assumptions.datetime_created,
    assumptions.pricing_method,
    assumptions.costing_method,
    assumptions.cost_tracker_project_list,
    assumptions.primary_manufacturing_location,
    assumptions.primary_manufacturing_type,
    assumptions.otd_late_reason_summary,
    assumptions.otd_late_reason_detail,
    assumptions.otp_late_reason_summary,
    assumptions.otp_late_reason_detail
   FROM assumptions
WITH DATA;

ALTER TABLE public.vw_demand_plan_new_analytics_attainment
    OWNER TO postgres;

GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment TO "avl-editor";
GRANT ALL ON TABLE public.vw_demand_plan_new_analytics_attainment TO postgres;
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment TO read_all;
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment TO "excel.loader";
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment TO "avl-reader";
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment TO "tableau-user";

CREATE INDEX vw_demand_plan_new_analytics_attainment_item_number_snapshot_da
    ON public.vw_demand_plan_new_analytics_attainment USING btree
    (item_number COLLATE pg_catalog."default", snapshot_date)
    TABLESPACE pg_default;
CREATE INDEX vw_demand_plan_new_analytics_attainment_scenario_index
    ON public.vw_demand_plan_new_analytics_attainment USING btree
    (scenario COLLATE pg_catalog."default")
    TABLESPACE pg_default;
    
    
    -- View: public.vw_demand_plan_analysis

-- DROP VIEW public.vw_demand_plan_analysis;

CREATE OR REPLACE VIEW public.vw_demand_plan_analysis
 AS
 SELECT vw_demand_plan_new_analytics_attainment.scenario,
    vw_demand_plan_new_analytics_attainment.snapshot_date,
    vw_demand_plan_new_analytics_attainment.is_warranty,
    vw_demand_plan_new_analytics_attainment.order_status_crd,
    vw_demand_plan_new_analytics_attainment.market,
    vw_demand_plan_new_analytics_attainment.na_forecast_family,
    vw_demand_plan_new_analytics_attainment.subfamily,
    vw_demand_plan_new_analytics_attainment.analytics,
    vw_demand_plan_new_analytics_attainment.planning_name,
    vw_demand_plan_new_analytics_attainment.item_number,
    vw_demand_plan_new_analytics_attainment.item_description,
    vw_demand_plan_new_analytics_attainment.ship_plan_month,
    vw_demand_plan_new_analytics_attainment.crd_plan_month,
    vw_demand_plan_new_analytics_attainment.consolidated_customer_name,
    vw_demand_plan_new_analytics_attainment.customer_name_bill_to,
    vw_demand_plan_new_analytics_attainment.project_name,
    vw_demand_plan_new_analytics_attainment.item_class,
    vw_demand_plan_new_analytics_attainment.na_business_unit,
    vw_demand_plan_new_analytics_attainment.crd_year,
    vw_demand_plan_new_analytics_attainment.ship_year,
    vw_demand_plan_new_analytics_attainment.salesperson,
    vw_demand_plan_new_analytics_attainment.hyperion_product_name AS onestream_product_name,
    vw_demand_plan_new_analytics_attainment.source_system,
    vw_demand_plan_new_analytics_attainment.plan_version,
    vw_demand_plan_new_analytics_attainment.customer_type,
    vw_demand_plan_new_analytics_attainment.datetime_created,
    vw_demand_plan_new_analytics_attainment.pricing_method,
    vw_demand_plan_new_analytics_attainment.costing_method,
    vw_demand_plan_new_analytics_attainment.cost_tracker_project_list,
    vw_demand_plan_new_analytics_attainment.primary_manufacturing_location,
    vw_demand_plan_new_analytics_attainment.primary_manufacturing_type,
    now() AS datetime_updated,
    sum(vw_demand_plan_new_analytics_attainment.total_tariff_cost) AS total_tariff_cost,
    sum(vw_demand_plan_new_analytics_attainment.total_cem_surcharges) AS total_cem_surcharges,
    sum(vw_demand_plan_new_analytics_attainment.total_vam_savings) AS total_vam_savings,
    sum(vw_demand_plan_new_analytics_attainment.total_base_material_cost) AS total_base_material_cost,
    sum(vw_demand_plan_new_analytics_attainment.total_freight_cost) AS total_freight_cost,
    sum(vw_demand_plan_new_analytics_attainment.total_cost_tracker_savings) AS total_cost_tracker_savings,
    sum(vw_demand_plan_new_analytics_attainment.quantity) AS quantity,
    sum(vw_demand_plan_new_analytics_attainment.total_sales) AS total_sales,
    sum(vw_demand_plan_new_analytics_attainment.total_standard_material_cost) AS total_standard_material_cost,
    sum(vw_demand_plan_new_analytics_attainment.total_material_margin) AS total_material_margin,
    vw_demand_plan_new_analytics_attainment.build_plan_month,
    sum(vw_demand_plan_new_analytics_attainment.build_plan_quantity) AS build_plan_quantity
   FROM vw_demand_plan_new_analytics_attainment
  WHERE ((vw_demand_plan_new_analytics_attainment.scenario = ANY (ARRAY['Current Forecast'::text, 'Budget'::text])) AND vw_demand_plan_new_analytics_attainment.ship_plan_month >= vw_demand_plan_new_analytics_attainment.snapshot_date OR vw_demand_plan_new_analytics_attainment.scenario = 'Actual'::text AND vw_demand_plan_new_analytics_attainment.order_status_crd = 'Billed'::text AND vw_demand_plan_new_analytics_attainment.ship_plan_month < (( SELECT make_date(dwhs_fiscaldates.fiscal_year_xylem_445, dwhs_fiscaldates.fiscal_month_xylem_445, 1) AS make_date
           FROM whs.dwhs_fiscaldates
          WHERE dwhs_fiscaldates.date_calendar = 'now'::text::date))) AND vw_demand_plan_new_analytics_attainment.ship_year::double precision >= date_part('YEAR'::text, 'now'::text::date) AND vw_demand_plan_new_analytics_attainment.ship_year::double precision <= (date_part('YEAR'::text, 'now'::text::date) + 1::double precision)
  GROUP BY vw_demand_plan_new_analytics_attainment.scenario, vw_demand_plan_new_analytics_attainment.snapshot_date, vw_demand_plan_new_analytics_attainment.is_warranty, vw_demand_plan_new_analytics_attainment.order_status_crd, vw_demand_plan_new_analytics_attainment.market, vw_demand_plan_new_analytics_attainment.na_forecast_family, vw_demand_plan_new_analytics_attainment.subfamily, vw_demand_plan_new_analytics_attainment.analytics, vw_demand_plan_new_analytics_attainment.planning_name, vw_demand_plan_new_analytics_attainment.item_number, vw_demand_plan_new_analytics_attainment.item_description, vw_demand_plan_new_analytics_attainment.ship_plan_month, vw_demand_plan_new_analytics_attainment.build_plan_month, vw_demand_plan_new_analytics_attainment.crd_plan_month, vw_demand_plan_new_analytics_attainment.consolidated_customer_name, vw_demand_plan_new_analytics_attainment.customer_name_bill_to, vw_demand_plan_new_analytics_attainment.project_name, vw_demand_plan_new_analytics_attainment.item_class, vw_demand_plan_new_analytics_attainment.na_business_unit, vw_demand_plan_new_analytics_attainment.crd_year, vw_demand_plan_new_analytics_attainment.ship_year, vw_demand_plan_new_analytics_attainment.salesperson, vw_demand_plan_new_analytics_attainment.hyperion_product_name, vw_demand_plan_new_analytics_attainment.source_system, vw_demand_plan_new_analytics_attainment.plan_version, vw_demand_plan_new_analytics_attainment.customer_type, vw_demand_plan_new_analytics_attainment.datetime_created, vw_demand_plan_new_analytics_attainment.pricing_method, vw_demand_plan_new_analytics_attainment.costing_method, vw_demand_plan_new_analytics_attainment.cost_tracker_project_list, vw_demand_plan_new_analytics_attainment.primary_manufacturing_location, vw_demand_plan_new_analytics_attainment.primary_manufacturing_type;

ALTER TABLE public.vw_demand_plan_analysis
    OWNER TO postgres;

GRANT SELECT ON TABLE public.vw_demand_plan_analysis TO "avl-editor";
GRANT ALL ON TABLE public.vw_demand_plan_analysis TO postgres;
GRANT SELECT ON TABLE public.vw_demand_plan_analysis TO read_all;
GRANT SELECT ON TABLE public.vw_demand_plan_analysis TO "excel.loader";
GRANT SELECT ON TABLE public.vw_demand_plan_analysis TO "avl-reader";
GRANT SELECT ON TABLE public.vw_demand_plan_analysis TO "tableau-user";



-- View: public.vw_demand_plan_new_analytics_attainment_view

-- DROP VIEW public.vw_demand_plan_new_analytics_attainment_view;

CREATE OR REPLACE VIEW public.vw_demand_plan_new_analytics_attainment_view
 AS
 WITH pb AS (
         SELECT base_product_code.planning_name,
            base_product_code.planning_name_id,
            array_to_string(array_agg(DISTINCT base_product_code.mrp_item ORDER BY base_product_code.mrp_item), ', '::text) AS mrp_item
           FROM whs.base_product_code
          WHERE base_product_code.mrp_item IS NOT NULL
          GROUP BY base_product_code.planning_name_id, base_product_code.planning_name
        )
 SELECT a.scenario,
    a.snapshot_date,
    a.is_warranty,
    a.order_status_crd,
    a.market,
    a.na_forecast_family,
    a.subfamily,
    a.analytics,
    a.planning_name,
    a.item_number,
    a.item_description,
    a.total_sales,
    a.quantity,
    a.ship_plan_month,
    a.revised_commit_date,
    a.crd_plan_month,
    a.crd_date,
    a.consolidated_customer_name,
    a.customer_name_bill_to,
    a.customer_name_ship_to,
    a.project_name,
    a.early_ship,
    a.order_number,
    a.order_line_number,
    a.order_with_line,
    a.unit_sales_price,
    a.unit_standard_material_cost,
    a.unit_material_margin,
    a.total_standard_material_cost,
    a.total_material_margin,
    a.item_class,
    a.na_business_unit,
    a.crd_year,
    a.ship_year,
    a.ship_quarter,
    a.date_entered,
    a.original_commit_date,
    a.hold_reason,
    a.planner_comments,
    a.salesperson,
    a.crd_quarter,
    a.salesforce_opportunity_name,
    a.planning_name_id,
    a.hyperion_product_name,
    a.source_system,
    a."Line ID",
    a.id,
    a.scenario_id,
    a.plan_revision_number,
    a.plan_version,
    a.project_code,
    a.customer_number_bill_to,
    a.ship_to_number,
    a.consolidated_customer_id,
    a.salesforce_account_id,
    a.salesforce_opportunity_id,
    a.date_invoiced,
    a.total_sales_current_plan,
    a.total_sales_previous_plan,
    a.total_sales_budget,
    a.total_material_cost_current_plan,
    a.total_material_cost_previous_plan,
    a.total_material_cost_budget,
    a.total_tariff_cost_current_plan,
    a.total_tariff_cost_previous_plan,
    a.total_tariff_cost_budget,
    a.total_freight_cost_current_plan,
    a.total_freight_cost_previous_plan,
    a.total_freight_cost_budget,
    a.total_base_material_cost_current_plan,
    a.total_base_material_cost_previous_plan,
    a.total_base_material_cost_budget,
    a.total_cost_tracker_savings_current_plan,
    a.total_cost_tracker_savings_previous_plan,
    a.total_cost_tracker_savings_budget,
    a.total_vam_savings_current_plan,
    a.total_vam_savings_previous_plan,
    a.total_vam_savings_savings_budget,
    a.total_cem_surcharges_current_plan,
    a.total_cem_surcharges_previous_plan,
    a.total_cem_surcharges_savings_budget,
    a.total_material_margin_current_plan,
    a.total_material_margin_previous_plan,
    a.total_material_margin_budget,
    a.total_quantity_current_plan,
    a.total_quantity_previous_plan,
    a.total_quantity_budget,
    a.total_cem_surcharges,
    a.total_vam_savings,
    a.total_base_material_cost,
    a.total_tariff_cost,
    a.total_freight_cost,
    a.total_cost_tracker_savings,
    a.customer_type,
    a.datetime_created,
    a.pricing_method,
    a.costing_method,
    a.cost_tracker_project_list,
    a.primary_manufacturing_location,
    a.primary_manufacturing_type,
    a.otd_late_reason_summary,
    a.otd_late_reason_detail,
    a.otp_late_reason_summary,
    a.otp_late_reason_detail,
    COALESCE(cmf2_1.cftlvl, 0::numeric) + COALESCE(cmf2_1.cfplvl, 0::numeric) AS cost_set_2_bk_1,
    COALESCE(cmf2_2.cftlvl, 0::numeric) + COALESCE(cmf2_2.cfplvl, 0::numeric) AS cost_set_2_bkt_2,
    COALESCE(cmf2_3.cftlvl, 0::numeric) + COALESCE(cmf2_3.cfplvl, 0::numeric) AS cost_set_2_bkt_3,
    COALESCE(cmf2_4.cftlvl, 0::numeric) + COALESCE(cmf2_4.cfplvl, 0::numeric) AS cost_set_2_bkt_4,
    COALESCE(cmf2_5.cftlvl, 0::numeric) + COALESCE(cmf2_5.cfplvl, 0::numeric) AS cost_set_2_bkt_5,
    COALESCE(cmf2_6.cftlvl, 0::numeric) + COALESCE(cmf2_6.cfplvl, 0::numeric) AS cost_set_2_bkt_6,
    COALESCE(cmf2_1.cftlvl, 0::numeric) + COALESCE(cmf2_1.cfplvl, 0::numeric) + COALESCE(cmf2_2.cftlvl, 0::numeric) + COALESCE(cmf2_2.cfplvl, 0::numeric) + COALESCE(cmf2_3.cftlvl, 0::numeric) + COALESCE(cmf2_3.cfplvl, 0::numeric) + COALESCE(cmf2_4.cftlvl, 0::numeric) + COALESCE(cmf2_4.cfplvl, 0::numeric) + COALESCE(cmf2_5.cftlvl, 0::numeric) + COALESCE(cmf2_5.cfplvl, 0::numeric) + COALESCE(cmf2_6.cftlvl, 0::numeric) + COALESCE(cmf2_6.cfplvl, 0::numeric) AS cost_set_2_total,
    COALESCE(cmf3_1.cftlvl, 0::numeric) + COALESCE(cmf3_1.cfplvl, 0::numeric) AS cost_set_3_bkt_1,
    COALESCE(cmf3_2.cftlvl, 0::numeric) + COALESCE(cmf3_2.cfplvl, 0::numeric) AS cost_set_3_bkt_2,
    COALESCE(cmf3_3.cftlvl, 0::numeric) + COALESCE(cmf3_3.cfplvl, 0::numeric) AS cost_set_3_bkt_3,
    COALESCE(cmf3_4.cftlvl, 0::numeric) + COALESCE(cmf3_4.cfplvl, 0::numeric) AS cost_set_3_bkt_4,
    COALESCE(cmf3_5.cftlvl, 0::numeric) + COALESCE(cmf3_5.cfplvl, 0::numeric) AS cost_set_3_bkt_5,
    COALESCE(cmf3_6.cftlvl, 0::numeric) + COALESCE(cmf3_6.cfplvl, 0::numeric) AS cost_set_3_bkt_6,
    COALESCE(cmf3_1.cftlvl, 0::numeric) + COALESCE(cmf3_1.cfplvl, 0::numeric) + COALESCE(cmf3_2.cftlvl, 0::numeric) + COALESCE(cmf3_2.cfplvl, 0::numeric) + COALESCE(cmf3_3.cftlvl, 0::numeric) + COALESCE(cmf3_3.cfplvl, 0::numeric) + COALESCE(cmf3_4.cftlvl, 0::numeric) + COALESCE(cmf3_4.cfplvl, 0::numeric) + COALESCE(cmf3_5.cftlvl, 0::numeric) + COALESCE(cmf3_5.cfplvl, 0::numeric) + COALESCE(cmf3_6.cftlvl, 0::numeric) + COALESCE(cmf3_6.cfplvl, 0::numeric) AS cost_set_3_total,
    pb.mrp_item,
    a.build_plan_month,
    a.build_plan_quantity
   FROM vw_demand_plan_new_analytics_attainment a
     LEFT JOIN whs.dwhs_cmf cmf2_1 ON a.item_number::text = cmf2_1.cfprod::text AND cmf2_1.cfcset = 2::numeric AND cmf2_1.cfcbkt = 1::numeric AND a.snapshot_date >= cmf2_1.begindate AND a.snapshot_date <= cmf2_1.enddate
     LEFT JOIN whs.dwhs_cmf cmf2_2 ON a.item_number::text = cmf2_2.cfprod::text AND cmf2_2.cfcset = 2::numeric AND cmf2_2.cfcbkt = 2::numeric AND a.snapshot_date >= cmf2_2.begindate AND a.snapshot_date <= cmf2_2.enddate
     LEFT JOIN whs.dwhs_cmf cmf2_3 ON a.item_number::text = cmf2_3.cfprod::text AND cmf2_3.cfcset = 2::numeric AND cmf2_3.cfcbkt = 3::numeric AND a.snapshot_date >= cmf2_3.begindate AND a.snapshot_date <= cmf2_3.enddate
     LEFT JOIN whs.dwhs_cmf cmf2_4 ON a.item_number::text = cmf2_4.cfprod::text AND cmf2_4.cfcset = 2::numeric AND cmf2_4.cfcbkt = 4::numeric AND a.snapshot_date >= cmf2_4.begindate AND a.snapshot_date <= cmf2_4.enddate
     LEFT JOIN whs.dwhs_cmf cmf2_5 ON a.item_number::text = cmf2_5.cfprod::text AND cmf2_5.cfcset = 2::numeric AND cmf2_5.cfcbkt = 5::numeric AND a.snapshot_date >= cmf2_5.begindate AND a.snapshot_date <= cmf2_5.enddate
     LEFT JOIN whs.dwhs_cmf cmf2_6 ON a.item_number::text = cmf2_6.cfprod::text AND cmf2_6.cfcset = 2::numeric AND cmf2_6.cfcbkt = 6::numeric AND a.snapshot_date >= cmf2_6.begindate AND a.snapshot_date <= cmf2_6.enddate
     LEFT JOIN whs.dwhs_cmf cmf3_1 ON a.item_number::text = cmf3_1.cfprod::text AND cmf3_1.cfcset = 3::numeric AND cmf3_1.cfcbkt = 1::numeric AND a.snapshot_date >= cmf3_1.begindate AND a.snapshot_date <= cmf3_1.enddate
     LEFT JOIN whs.dwhs_cmf cmf3_2 ON a.item_number::text = cmf3_2.cfprod::text AND cmf3_2.cfcset = 3::numeric AND cmf3_2.cfcbkt = 2::numeric AND a.snapshot_date >= cmf3_2.begindate AND a.snapshot_date <= cmf3_2.enddate
     LEFT JOIN whs.dwhs_cmf cmf3_3 ON a.item_number::text = cmf3_3.cfprod::text AND cmf3_3.cfcset = 3::numeric AND cmf3_3.cfcbkt = 3::numeric AND a.snapshot_date >= cmf3_3.begindate AND a.snapshot_date <= cmf3_3.enddate
     LEFT JOIN whs.dwhs_cmf cmf3_4 ON a.item_number::text = cmf3_4.cfprod::text AND cmf3_4.cfcset = 3::numeric AND cmf3_4.cfcbkt = 4::numeric AND a.snapshot_date >= cmf3_4.begindate AND a.snapshot_date <= cmf3_4.enddate
     LEFT JOIN whs.dwhs_cmf cmf3_5 ON a.item_number::text = cmf3_5.cfprod::text AND cmf3_5.cfcset = 3::numeric AND cmf3_5.cfcbkt = 5::numeric AND a.snapshot_date >= cmf3_5.begindate AND a.snapshot_date <= cmf3_5.enddate
     LEFT JOIN whs.dwhs_cmf cmf3_6 ON a.item_number::text = cmf3_6.cfprod::text AND cmf3_6.cfcset = 3::numeric AND cmf3_6.cfcbkt = 6::numeric AND a.snapshot_date >= cmf3_6.begindate AND a.snapshot_date <= cmf3_6.enddate
     LEFT JOIN pb ON a.planning_name_id::text = pb.planning_name_id::text
  WHERE a.scenario !~~ 'Previous Plan%'::text;

ALTER TABLE public.vw_demand_plan_new_analytics_attainment_view
    OWNER TO postgres;

GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment_view TO "avl-editor";
GRANT ALL ON TABLE public.vw_demand_plan_new_analytics_attainment_view TO postgres;
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment_view TO read_all;
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment_view TO "excel.loader";
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment_view TO "avl-reader";
GRANT SELECT ON TABLE public.vw_demand_plan_new_analytics_attainment_view TO "tableau-user";
