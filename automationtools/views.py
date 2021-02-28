from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

# Create your views here.
def report_home(request):

    return render(request, "report_home.html", context={"test": "hello world"})


def get_top_sellers(request):
    sql = """
        WITH top_sellers AS (
            SELECT
                product_sku,
                SUM(quantity) as quantity
            FROM
                report_moondance.sales_orders
            WHERE   
                product_category = 'Bar Soaps' AND
                processed_date >= '2020-10-01'
            GROUP BY
                product_sku
            ORDER BY
                2 DESC
            LIMIT 
                10
        )
        ,detail AS (
            SELECT  
                product_description,
                processed_date::DATE as date_sold, 
                SUM(so.quantity) as quantity
            FROM
                report_moondance.sales_orders so JOIN
                top_sellers ON so.product_sku = top_sellers.product_sku
            GROUP BY
                1,2
        )

        SELECT
            JSON_AGG(ROW_TO_JSON(row)) as series
        FROM
            (
                SELECT
                    product_description as name,
                    JSON_AGG(JSONB_BUILD_ARRAY(date_sold, quantity) ORDER BY date_sold) as data
                FROM
                    detail
                GROUP BY
                    1
            ) row
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        json_data = cursor.fetchall()[0]

    return HttpResponse(json_data , content_type="application/json")