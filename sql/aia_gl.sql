   SELECT
        currencytype,
        accountingcurrencycode,
        accountingcurrencyamount,
        transactioncurrencycode,
        transactioncurrencyamount,
        m.ledgerpostingtype,
        m.generalledgeraccountcategory,
        AllAIA_09,
        account.*,
        m.*
    FROM
        financials.vwGeneralLedgerTransactions M
        LEFT JOIN datamart.Dimensions.ReportingEntity R on 
            M.DivisionId = R.DivisionId and 
            M.DepartmentId = R.DepartmentId and 
            M.LegalEntityId = R.LegalEntityId and 
            M.TechnologyId = R.TechnologyId
        JOIN datamart.dimensions.dates dates ON m.accountingdate = dates.date
        LEFT JOIN datamart.dimensions.GeneralLedgerAccounts account ON 
            m.glaccountid = account.GeneralLedgerAccountID
    WHERE
        --R.AllAIA_09 = 'Digital Solutions' and
       -- m.glaccountid = '77030' and
         ledger <> 'CUSD' and
       --  m.glaccountid IN ('52520','77800') and
      --  dates.fiscalyear = 2020 and
/*                ledgerpostingtype IN (
            'Intercompany accounting                                         ',
            'Sales tax                                                       ',
            'Project - cost                                                  ',
            'Project - payroll allocation                                    ',
            'Project - invoiced revenue                                      ',
            'Project - accrued revenue - sales value                         ',
            'Project - WIP - sales value                                     ',
            'Never ledger                                                    ',
            'Project - WIP invoiced - on account                             '
        
        ) AND*/
       -- accountingdate = '2020-08-27' and
/*        AND m.glaccountid = 52585
        AND m.divisionid = 73 */
       vouchernumber = 'PTUS-TSV-063088' --and
        -- accountingdate = '2020-09-19' and
        -- m.glaccountid IN (52520, 77800)

  