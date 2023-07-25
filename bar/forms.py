# bar/forms.py

from django import forms
from .models import Drink, Category

class DrinkForm(forms.ModelForm):
    class Meta:
        model = Drink
        fields = ['name', 'price', 'quantity_in_stock', 'category']  # Include 'category' field

class DrinkFilterForm(forms.Form):
    name = forms.CharField(label='Filter by Name', required=False)
    category = forms.ModelChoiceField(label='Filter by Category', queryset=Category.objects.all(), required=False)
