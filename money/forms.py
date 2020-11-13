from django import forms
        
from money.models import Accounts, Products, RANGE_RECOMENDATION_CHOICES



class AccountsTransferForm(forms.Form):
    datetime = forms.DateTimeField(required=True)
    destiny = forms.ModelChoiceField(queryset=Accounts.objects.all().filter(active=True), required=True)
    amount=forms.DecimalField(min_value=0, decimal_places=2, required=True)
    commission=forms.DecimalField(min_value=0, decimal_places=2, required=True)

class ProductsRangeForm(forms.Form):

    products = forms.ModelChoiceField(queryset=Products.qs_products_of_investments(), required=True)
    percentage_between_ranges = forms.DecimalField(min_value=0, decimal_places=2, required=True)
    percentage_gains=forms.DecimalField(min_value=0, decimal_places=2, required=True)
    amount_to_invest=forms.DecimalField(min_value=0, decimal_places=2, required=True)
    recomendation_methods = forms.ChoiceField(choices=RANGE_RECOMENDATION_CHOICES, required=True)
    
