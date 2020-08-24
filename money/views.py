from datetime import datetime
from django.urls import reverse_lazy
from django.contrib.auth import  login
from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView#, DeleteView

from money.connection_dj import cursor_rows
from money.forms import SignUpForm    
from money.models import Banks, Accounts, Investments, Investmentsoperations, Dividends, Concepts
from money.settingsdb import settingsdb
from money.tabulator import tb_listdict, tb_queryset
from money.tables import TabulatorInvestmentsOperationsCurrent, TabulatorInvestmentsOperations, TabulatorInvestments, TabulatorAccounts
from money.tokens import account_activation_token


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


@login_required
def concept_list(request):
    list_concepts= tb_queryset(Concepts.objects.all().order_by('name'))
    return render(request, 'concept_list.html', locals())

def error_403(request, exception):
        data = {}
        return render(request,'403.html', data)

## @todo Add search to search field to repeat search
## @todo Limit search minimum 3 and maximum 50
## @todo Add a tab Widget, author, books, valorations with number in ttab
def home(request):
    return render(request, 'home.html', locals())



@login_required
def bank_list(request,  active=True):
    banks= list(Banks.objects.all().filter(active=active).order_by('name').values())
    return render(request, 'bank_list.html', locals())
    
@login_required
def account_list(request,  active=True):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    
    accounts= Accounts.objects.all().filter(active=active).order_by('name')
    
    list_accounts=[]
    for account in accounts:
        balance=account.balance(datetime.now())
        list_accounts.append({
                "id": account.id, 
                "active":account.active, 
                "name": account.fullName(), 
                "number": account.number,
                "balance": balance[0].string(),  
                "balance_user": balance[1], 
            }
        )
    
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, local_currency).render()
    #balance is aligned left(text) I can do it too with javascript.
    table_accounts=table_accounts.replace(', field:"balance"', ', field:"balance", align:"right"')
    return render(request, 'account_list.html', locals())
        
@login_required
def investment_list(request,  active):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    investments= Investments.objects.all().filter(active=active).order_by('name')
    table_inv=TabulatorInvestments("I", "investment_view", investments, local_currency).render()

    return render(request, 'investment_list.html', locals())
    
@login_required
def investment_view(request, pk):
    investment=get_object_or_404(Investments, id=pk)
    oi=Investmentsoperations.objects.all().filter(investments_id=pk).order_by('datetime')
    table_io=TabulatorInvestmentsOperations("IO", "bank_update", oi, investment).render()
    
    oic=cursor_rows("select * from investment_operations_current({},now());".format(pk))
    table_ioc=TabulatorInvestmentsOperationsCurrent("IOC", "bank_update", oic, investment).render()

    oih=cursor_rows("select * from investment_operations_historical({},now());".format(pk))
    list_oih=tb_listdict(oih)
    dividends=Dividends.objects.all().filter(investments_id=pk).order_by('datetime')
    list_dividends=tb_queryset(dividends)        
    return render(request, 'investment_view.html', locals())
    
@login_required
def bank_new(request, pk):
    return render(request, 'bank_new.html', locals())
  
@method_decorator(login_required, name='dispatch')
class bank_update(UpdateView):
    model = Banks
    fields = ['name', 'active']
    template_name="bank_update.html"

    def get_success_url(self):
        return reverse_lazy('bank_list')
    
@login_required
def bank_view(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'bank_view.html', locals())
    

@login_required
def bank_delete(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'bank_delete.html', locals())
