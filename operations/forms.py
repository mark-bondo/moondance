from django import forms
from django_select2 import forms as s2forms
from .models import (
    Raw_Material_Proxy,
    Product,
    Labor_Proxy,
    Finished_Goods_Proxy,
    Labor_Rates,
    LABOR_TYPES,
    SALES_CHANNEL_TYPES,
)

unit_of_measure_choices = (
    ("each", "each"),
    ("minutes", "minutes",)
)

class Raw_Material_Proxy_Form(forms.ModelForm):
    model = Raw_Material_Proxy
    product_type_list = (
        ("Raw Materials", "Raw Materials"),
        ("WIP", "WIP"),
        ("Labor", "Labor"),
    )
    product_type = forms.ChoiceField(choices=product_type_list, initial="Raw Materials")


class Labor_Proxy_Form(forms.ModelForm):
    model = Labor_Proxy
    product_type_list = (
        ("Labor", "Labor"),
    )
    product_type = forms.ChoiceField(choices=product_type_list, initial="Labor")
    unit_of_measure = forms.ChoiceField(choices=unit_of_measure_choices)


class Finished_Goods_Proxy_Form(forms.ModelForm):
    model = Finished_Goods_Proxy
    product_type_list = (
        ("Finished Goods", "Finished Goods"),
    )
    product_type = forms.ChoiceField(choices=product_type_list, initial="Finished Goods")


class Labor_Rates_Form(forms.ModelForm):
    model = Labor_Rates
    labor_type = forms.ChoiceField(choices=LABOR_TYPES, required=True)
    sales_channel_type = forms.ChoiceField(choices=SALES_CHANNEL_TYPES, required=True, initial="All")