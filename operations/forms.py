from django import forms
from .models import Materials_Management_Proxy

class Materials_Management_Proxy_Form(forms.ModelForm):
    model = Materials_Management_Proxy
    product_type_list = (
        ("WIP", "WIP"),
        ("Raw Materials",  "Raw Materials"),
    )

    product_type = forms.ChoiceField(choices=product_type_list)
