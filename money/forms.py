from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
        
from money.models import Accountsoperations, Accounts, Products, RANGE_RECOMENDATION_CHOICES

from xulpymoney.libxulpymoneytypes import eOperationType

class AccountsOperationsForm(forms.ModelForm):
    class Meta:
        model = Accountsoperations
        fields = ( 'datetime', 'concepts',  'amount', 'accounts', 'comment')

    def clean(self):      
        cleaned_data = super(AccountsOperationsForm, self).clean()
        if cleaned_data['concepts'].operationstypes.id==eOperationType.Expense and cleaned_data.get("amount")>=0:
            raise ValidationError(_('Invalid value: %(value)s, must be negative'),code='invalid',  params={'value': cleaned_data['amount']},)
        if cleaned_data['concepts'].operationstypes.id==eOperationType.Income and cleaned_data.get("amount")<0:
            raise ValidationError(_('Invalid value: %(value)s, must be positive'),code='invalid',  params={'value': cleaned_data['amount']},)
        return cleaned_data

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
    
