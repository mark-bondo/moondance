import json
from django.db import connection
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def product_hook(request, object, action):
    item = json.loads(request.body)

    object_map = {
        "product": "shopify.shopify_product",
        "order": "shopify.shopify_sales_order",
        "customer": "shopify.shopify_customer",
    }

    # with open("test.json", "w") as w:
    #     w.write(str(request.META))

    if action == "delete":
        with connection.cursor() as cursor:
            sql = """
                UPDATE
                    %(table)s
                SET
                    _active = FALSE,
                    _last_updated = NOW()
                WHERE
                    id = %(id)s
                ;
            """ % {
                "id": int(item["id"]),
                "table": object_map[object],
            }
            cursor.execute(sql)

    return HttpResponse(item["id"])
