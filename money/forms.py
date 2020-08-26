from django.contrib.auth.models import User
from money.models import Accountsoperations

    
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm

from xulpymoney.libxulpymoneytypes import eOperationType
from django.core.exceptions import ValidationError
from django import forms
        

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

                
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
        
