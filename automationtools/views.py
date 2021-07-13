from integration.models import Shopify_Product
import json


def product_hook(request, action):
    item = json.loads(request.body)

    if item.action == "delete":
        p = Shopify_Product.objects.get(id=item.id)
        p._active = False
        p.save()
