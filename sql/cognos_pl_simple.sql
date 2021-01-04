SELECT
    period,
    orderno,
    --sa.name as brand,
    --phase_ii,
    CASE WHEN phase_ii = 'Resale_3rd_Pty_Transport' AND sa = 'S2' THEN 'Sanitaire_Aeration_Prod' END,
    pc,
    CASE
        WHEN 
            phase_ii = 'UV_System' AND 
            COALESCE(phase_ii, '') NOT IN ( -- SANITAIRE
                '3rd_Party_Service_Treatment',
                'Flygt_Mixer_Accessories',
                'Flygt_Mixer_Parts',
                'Flygt_Mixers_Prod',
                'Ozone_Service',
                'Sanitaire_Service',
                'ANLY_Other',
                'Aeration_Service' -- doesn't match p2 table
            ) THEN
            CASE
                WHEN sa ILIKE 'R%' AND COALESCE(projectno, '') ILIKE 'Z%' THEN 'OZ_System'
                WHEN sa ILIKE 'R%' AND COALESCE(projectno, '') NOT ILIKE ALL(ARRAY['Z%', 'U%']) AND COALESCE(pc, '') ILIKE 'W2%' THEN 'OZ_Parts'
                WHEN sa ILIKE 'R%' AND COALESCE(projectno, '') NOT ILIKE ALL(ARRAY['Z%', 'U%']) AND COALESCE(pc, '') NOT ILIKE 'W2%' THEN 'UV_Parts'
                ELSE phase_ii
            END
        WHEN
            sa.name = 'SANITAIRE' AND 
            COALESCE(phase_ii, '') NOT IN ( -- SANITAIRE
                '3rd_Party_Service_Treatment',
                'Flygt_Mixer_Accessories',
                'Flygt_Mixer_Parts',
                'Flygt_Mixers_Prod',
                'Ozone_Service',
                'Sanitaire_Service',
                'ANLY_Other',
                'Aeration_Service' -- doesn't match p2 table
            ) THEN
            CASE
                WHEN sa = 'S2' AND COALESCE(projectno, '') NOT ILIKE ALL(ARRAY['1%', '2%']) THEN 'Sanitaire_Parts'
                WHEN sa = 'S2' AND COALESCE(projectno, '') ILIKE '%TC' THEN 'Sanitaire_Parts'
                ELSE phase_ii
            END
        WHEN phase_ii = 'Resale_3rd_Pty_Transport' AND sa = 'S2' THEN 'Sanitaire_Aeration_Prod'
        ELSE
            phase_ii
    END,
    --pc,
    SUM(sls_amt * splt_percent::NUMERIC) as sales,
    SUM(inv_cost) as cost,
    count(*)
FROM
    "steeb"."steeb_invyearlyf" i
    LEFT JOIN public.datamanager_property_values sa ON i.sa = sa.value AND dimension_id = 154
WHERE
    period = '2011'-- AND
    --sa.name NOT IN ('LAR', 'IC') AND
   -- COALESCE(nonssl030, '') != 'Y' --AND
    --tran_type NOT ILIKE ALL(ARRAY['W1', 'W2', 'W5', 'X%'])
    AND CASE WHEN phase_ii = 'Resale_3rd_Pty_Transport' AND sa = 'S2' THEN TRUE END = TRUE
GROUP BY
    1,2,3,4,5
ORDER BY
    2, 3
/*WHERE
    sa = 'L1' AND (
    pl NOT ILIKE 'P%' OR
    projectno  LIKE 'I%'
    )*/
    
    