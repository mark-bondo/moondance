import json
from django.db import connection
from django.http.response import HttpResponse
from integration.models import Shopify_Product
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def product_hook(request, action):
    item = json.loads(request.body)

    if item["action"] == "delete":
        with connection.cursor() as cursor:
            sql = """
                UPDATE
                    shopify.shopify_product
                SET
                    _active = FALSE,
                    _updated = NOW()
                WHERE
                    id = %s
                ;
            """
            cursor.execute(sql, item["id"])

    return HttpResponse(item["id"])
