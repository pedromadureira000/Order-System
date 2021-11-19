from django import forms
from erp.orders.models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ()
