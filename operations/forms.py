from django import forms
from django_select2 import forms as s2forms
from .models import (
    Materials_Management_Proxy,
    Product,
    Finished_Goods_Proxy
)

class Materials_Management_Proxy_Form(forms.ModelForm):
    model = Materials_Management_Proxy
    product_type_list = (
        ("Raw Materials", "Raw Materials"),
        ("WIP", "WIP"),

    )
    product_type = forms.ChoiceField(choices=product_type_list, initial="Raw Materials")


class Finished_Goods_Proxy_Form(forms.ModelForm):
    model = Finished_Goods_Proxy
    product_type_list = (
        ("Finished Goods", "Finished Goods"),
    )
    product_type = forms.ChoiceField(choices=product_type_list, initial="Finished Goods")