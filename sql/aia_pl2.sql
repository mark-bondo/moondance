    SELECT
        dates.fiscalyear,
        dates.fiscalmonth,
        R.AllAIA_09,
        R.AllAIA_06,
        Level_1,
        Level_2,
        Level_3,
        Level_4,
        Level_5,
        Level_6,
        CASE
            WHEN level_2 IN (
                'Direct Costs', 
                'Direct - Intercompany COS', 
                'Direct - Intercompany Revenue',
                'Direct Project Labour'
            ) THEN 'Cost of Sales'
            WHEN level_2 IN ('IC Time and Attendance Cost', 'IC Time and Attendance Recharge') THEN 'E&O'
            WHEN level_2 IN ('COS Amortization') THEN 'Cost of Sales Amortization'
            WHEN level_3 IN('Other Operating Expense', '(Gain) Loss on Foreign Exchange', 'Other Income') THEN 'Other Operating Income & Expenses'
            WHEN GeneralLedgerAccountType = 'Revenue' THEN GeneralLedgerAccountType
            WHEN Level_4 <> 'Operating Income' OR generalledgeraccountcategory = 'Impairment' THEN 'Non-Operating Income & Expenses'
            ELSE departmentgroup
        END as functional_area,
        CASE
            WHEN level_2 IN (
                'Direct Costs', 
                'Direct - Intercompany COS', 
                'Direct - Intercompany Revenue',
                'Direct Project Labour'

            ) THEN 'Cost of Sales'
            WHEN level_2 IN ('COS Amortization') THEN 'Cost of Sales Amortization'
            ELSE account.GeneralLedgerAccountType 
         END as GeneralLedgerAccountType,
        --m.accountingdate as ledgerdate,
        --m.VoucherNumber,
        account.GeneralLedgerAccountCategory,

        m.glaccountid + ' - ' + GeneralLedgerAccountDescription as gl_account,
        m.DivisionId,
        m.TechnologyId,
        m.legalentityid,
        m.departmentid,
        RTRIM(pt.description) as ledgerpostingtype,
/*        CASE
            WHEN RTRIM(pt.description) IN ('Intercompany cost', 'Sales Tax') THEN 'Project - cost'
            ELSE RTRIM(pt.description)
        END as ledgerpostingtype,*/
        CASE
            WHEN RTRIM(pt.description) IN (
                'Intercompany cost',
                'Project - cost',
                'Project - cost - item',
                'Project - payroll allocation',
                'Project - accrued loss',
                'Project - accrued revenue - sales value',
                'Project - accrued revenue - sales value',
                'Project - invoiced on-account',
                'Project - invoiced revenue',
                'Sales tax'
            ) THEN 'Projects'
            ELSE 'Unassigned'
        END as ledgerpostingsource,
        CAST(sum(AccountingCurrencyAmount) AS NUMERIC(16, 2)) as total_amount_local,
        CAST(sum(AccountingCurrencyAmount * xa.exchangerate) AS NUMERIC(16, 2)) as total_amount_usd
    FROM
        financials.GeneralLedgerTransactions m
        JOIN Enum.LedgerPostingType pt ON m.LedgerPostingTypeEnum = pt.Id
        JOIN datamart.dimensions.dates dates ON m.accountingdate = dates.date
        JOIN datamart.dimensions.GeneralLedgerAccounts account ON m.glaccountid = account.GeneralLedgerAccountID
        LEFT JOIN datamart.Dimensions.ReportingEntity r on 
            m.DivisionId = r.DivisionId and 
            m.DepartmentId = r.DepartmentId and 
            m.LegalEntityId = r.LegalEntityId and 
            m.TechnologyId = r.TechnologyId
        LEFT JOIN datamart.ExchangeRates.MonthAverageRatesCompiled xa ON 
            m.AccountingCurrencyCode = xa.FromCurrencyCode AND 
            m.accountingdate BETWEEN xa.PeriodStartDate AND xa.PeriodEndDate
        LEFT JOIN datamart.dimensions.GeneralLedgerAccount_Hierarchy_NetIncome ni ON m.glaccountid = ni.GeneralLedgerAccountId
    WHERE
        dates.fiscalYear = 2020 AND
        m.ledger <> 'CUSD' AND
        account.IncomeStatementOrBalanceSheet = 'Income Statement' AND
        
        /*
        (
            (
                RTRIM(pt.description) IN (
                    'Intercompany cost',
                    'Project - cost',
                    'Project - cost - item',
                    'Project - payroll allocation',
                    'Project - accrued loss',
                    'Project - accrued revenue - sales value',
                    'Project - accrued revenue - sales value',
                    'Project - invoiced on-account',
                    'Project - invoiced revenue'
                )
            ) 
            
            OR
            
            (
                RTRIM(pt.description) IN (
                    'Sales tax'
                ) AND
                account.GeneralLedgerAccountCategory <> 'Intercompany Expense'
            )
        )*/
        R.AllAIA_09 = 'Digital Solutions'
    GROUP BY
        dates.fiscalyear,
        dates.fiscalmonth,
       -- m.accountingdate,
        --m.VoucherNumber,
                account.GeneralLedgerAccountCategory,
        account.GeneralLedgerAccountType ,
        R.AllAIA_09,
        R.AllAIA_06,
        Level_1,
        Level_2,
        Level_3,
        Level_4,
        Level_5,
        Level_6,
        CASE
            WHEN level_2 IN (
                'Direct Costs', 
                'Direct - Intercompany COS', 
                'Direct - Intercompany Revenue',
                'Direct Project Labour'
            ) THEN 'Cost of Sales'
            WHEN level_2 IN ('IC Time and Attendance Cost', 'IC Time and Attendance Recharge') THEN 'E&O'
            WHEN level_2 IN ('COS Amortization') THEN 'Cost of Sales Amortization'
            WHEN level_3 IN('Other Operating Expense', '(Gain) Loss on Foreign Exchange', 'Other Income') THEN 'Other Operating Income & Expenses'
            WHEN GeneralLedgerAccountType = 'Revenue' THEN GeneralLedgerAccountType
            WHEN Level_4 <> 'Operating Income' OR generalledgeraccountcategory = 'Impairment' THEN 'Non-Operating Income & Expenses'
            ELSE departmentgroup
        END,
        m.glaccountid + ' - ' + GeneralLedgerAccountDescription,
        m.DivisionId,
        m.TechnologyId,
        m.legalentityid,
        m.departmentid,
        RTRIM(pt.description),
/*        CASE
            WHEN RTRIM(pt.description) IN ('Intercompany cost', 'Sales Tax') THEN 'Project - cost'
            ELSE RTRIM(pt.description)
        END,*/
        CASE
            WHEN level_2 IN (
                'Direct Costs', 
                'Direct - Intercompany COS', 
                'Direct - Intercompany Revenue',
                'Direct Project Labour'

            ) THEN 'Cost of Sales'
            WHEN level_2 IN ('IC Time and Attendance Cost') THEN 'E&O'
            WHEN level_2 IN ('COS Amortization') THEN 'Cost of Sales Amortization'
            ELSE departmentgroup
        END,
        CASE
            WHEN level_2 IN (
                'Direct Costs', 
                'Direct - Intercompany COS', 
                'Direct - Intercompany Revenue',
                'Direct Project Labour'

            ) THEN 'Cost of Sales'
            WHEN level_2 IN ('COS Amortization') THEN 'Cost of Sales Amortization'
            ELSE account.GeneralLedgerAccountType 
         END