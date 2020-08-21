from django.contrib.auth.models import User

    
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.forms import UserCreationForm

from django import forms
        

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )