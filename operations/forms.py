from django import forms
from .models import Materials_Management_Proxy, Product
from django_select2 import forms as s2forms

class Materials_Management_Proxy_Form(forms.ModelForm):
    model = Materials_Management_Proxy
    product_type_list = (
        ("Raw Materials",  "Raw Materials"),
        ("WIP", "WIP"),

    )
    product_type = forms.ChoiceField(choices=product_type_list, initial="Raw Materials")
