from django import forms
from .models import Restaurant, Table


class RestaurantForm(forms.ModelForm):
    """
    Form for creating/updating restaurant information
    """
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'phone', 'logo', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TableForm(forms.ModelForm):
    """
    Form for creating/updating tables
    """
    class Meta:
        model = Table
        fields = ['name', 'seats', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 