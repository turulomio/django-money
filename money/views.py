#from django import forms
#from django.db import connection
#from django.db.models import Q, Avg, F
#from django.contrib.auth.decorators import login_required, permission_required
#from django.http import HttpResponseRedirect
#from django.urls import reverse_lazy
#from django.utils.translation import gettext_lazy as _
#from django.utils.decorators import method_decorator
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
#
#from books.forms import BookAddForm, ValorationAddForm
#from books.models import Author,  Book, Valoration

from django.urls import reverse_lazy
from django.contrib.auth import  login
from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from .models import Banks

from .tokens import account_activation_token

from .forms import SignUpForm    

## View to register a new user
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = """Hi {},\n\nPlease click on the link below to confirm your registration:\n\nhttp://{}{}""".format(
                    user.username, 
                    current_site.domain, 
                    reverse_lazy(   'activate', 
                                            kwargs={ 'uidb64': urlsafe_base64_encode(force_bytes(user.pk)) , 
                                                            'token': account_activation_token.make_token(user)
                                                          }
                                        )
                    )

            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'account_activation_sent.html') 
    
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return render(request, 'account_activation_valid.html')
    else:
        return render(request, 'account_activation_invalid.html')



def error_403(request, exception):
        data = {}
        return render(request,'403.html', data)

## @todo Add search to search field to repeat search
## @todo Limit search minimum 3 and maximum 50
## @todo Add a tab Widget, author, books, valorations with number in ttab
def home(request):
    return render(request, 'home.html', locals())



@login_required
def bank_list(request):
    banks= Banks.objects.all().order_by('name')
    return render(request, 'bank_list.html', locals())
    
    
    
def bank_new(request, pk):
    return render(request, 'money/bank_new.html', locals())
def bank_view(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'money/bank_view.html', locals())
def bank_update(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'money/bank_update.html', locals())
def bank_delete(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'money/bank_delete.html', locals())
