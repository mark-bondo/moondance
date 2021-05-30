from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required


# Create your views here.
def report_home(request):
    return render(request, "report_home.html", context={"test": "hello world"})


@login_required
def get_top_sellers(request):
    sql = """
        WITH top_sellers AS (
            SELECT
                product_description,
                SUM(quantity) as quantity
            FROM
                report_moondance.sales_orders
            WHERE
                product_category = 'Bar Soaps' AND
                processed_date >= '2020-10-01'
            GROUP BY
                1
            ORDER BY
                2 DESC
            LIMIT 
                5
        )
        ,detail AS (
            SELECT  
                so.product_description as name,
                DATE_TRUNC('MONTH', processed_date)::date as date_sold,
                SUM(so.quantity) as quantity
            FROM
                report_moondance.sales_orders so JOIN
                top_sellers ON so.product_description = top_sellers.product_description
            WHERE
                processed_date >= '2020-10-01'
            GROUP BY
                1,2
        )

        SELECT
            JSONB_BUILD_OBJECT('series', JSON_AGG(ROW_TO_JSON(row))) as series
        FROM
            (
                SELECT
                    name,
                    'column' as type,
                    JSON_AGG(JSONB_BUILD_ARRAY(date_sold, quantity) ORDER BY date_sold) as data
                FROM
                    detail
                GROUP BY
                    1,2
            ) row
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data, content_type="application/json")
