import json
from django.db import connection
from integration.models import Shopify_Product
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def product_hook(request, action):
    # item = json.loads(request.body)

    with open("test.json", "w") as w:
        w.write(request.body)

    # if item.action == "delete":
    #     products = Shopify_Product.objects.filter(id=item.id)

    #     for p in products:
    #         p._active = False
    #         p.save()
