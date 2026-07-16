# accounts/forms.py
from django import forms
from .models import BusinessProfile, Customer

class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['business_type', 'investment', 'expected_profit', 'actual_profit', 'start_date', 'end_date']
        widgets = {
            'business_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Retail, Wholesale, etc.'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'business_type': 'Business Type',
            'investment': 'Investment (₹)',
            'expected_profit': 'Expected Profit (₹)',
            'actual_profit': 'Actual Profit (₹)',
        }

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['mobile', 'profile_photo']