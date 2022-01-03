from django import forms
from orders.models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ()
