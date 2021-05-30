from django import forms
from .models import (
    Raw_Material_Proxy,
    Product_Code,
    Labor_Code,
    Labor_Proxy,
    Finished_Goods_Proxy,
    SALES_CHANNEL_TYPES,
)


class Labor_Proxy_Form(forms.ModelForm):
    model = Labor_Proxy

    unit_of_measure_choices = (
        (
            "each",
            "each",
        ),
        (
            "minutes",
            "minutes",
        ),
    )
    unit_of_measure = forms.ChoiceField(choices=unit_of_measure_choices)


class Raw_Material_Proxy_Form(forms.ModelForm):
    model = Raw_Material_Proxy


class Finished_Goods_Proxy_Form(forms.ModelForm):
    model = Finished_Goods_Proxy


class Product_Code_Form(forms.ModelForm):
    model = Product_Code

    type_list = (
        ("Finished Goods", "Finished Goods"),
        ("Raw Materials", "Raw Materials"),
        ("WIP", "WIP"),
    )
    type = forms.ChoiceField(choices=type_list, required=True)


class Labor_Code_Form(forms.ModelForm):
    model = Labor_Code

    type_list = (
        ("Labor", "Labor"),
        (
            "WIP - Labor",
            "WIP - Labor",
        ),
    )
    type = forms.ChoiceField(choices=type_list, initial="Labor", required=True)
    sales_channel_type = forms.ChoiceField(
        choices=SALES_CHANNEL_TYPES, required=True, initial="All"
    )
