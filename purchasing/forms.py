from .models import Inventory_Onhand, LOCATION_LIST
from django import forms


class Inventory_Onhand_Form(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     location_list = [(None, '--------')] + LOCATION_LIST.copy()
    #     if self.location:
    #         for i, loc in enumerate(location_list):
    #             if self.location == loc[0]:
    #                 del location_list[i]
    #                 break

    #     self.fields['to_location'].choices = location_list

    def clean(self):
        data = self.cleaned_data

        location = data.get('location')
        to_location = data.get('to_location')
        transfer_quantity = data.get('transfer_quantity')
        quantity_onhand = data.get('quantity_onhand')

        if transfer_quantity:
            if not to_location:
                msg = "A Transfer location is required"
                self.add_error('to_location', msg)
            if to_location == location:
                msg = "Cannot transfer to the same location"
                self.add_error('to_location', msg)
            if transfer_quantity <= 0:
                msg = "Transfer quantity must be greater than zero"
                self.add_error('transfer_quantity', msg)
            elif transfer_quantity > quantity_onhand:
                msg = "Transfer quantity cannot exceed inventory onhand"
                self.add_error('transfer_quantity', msg)
        
    class Meta:
        model = Inventory_Onhand
        fields = (
            "location",
            "sku",
            "quantity_onhand",
            "to_location",
            "transfer_quantity",
        )