from datetime import  date
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import  login
from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView, CreateView, DeleteView
#from django.http import HttpResponseRedirect
from django import forms

from money.connection_dj import cursor_rows
from money.forms import SignUpForm
from money.models import Banks, Accounts, Accountsoperations, Creditcards,  Investments, Investmentsoperations, Dividends, Concepts, Products,  Orders
from money.settingsdb import settingsdb
from money.tabulator import  tb_queryset
from money.tables import TabulatorInvestmentsOperationsCurrent, TabulatorInvestmentsOperations, TabulatorInvestments, TabulatorAccounts, TabulatorInvestmentsOperationsHistorical, TabulatorAccountOperations, TabulatorCreditCards,  TabulatorConcepts, TabulatorBanks, TabulatorOrders
from money.tokens import account_activation_token
from money.reusing.datetime_functions import dtaware_month_start

@login_required
def order_list(request,  active):
    if active is True:
        orders= Orders.objects.all().filter(executed__isnull=True ,  expiration__gte=date.today()).order_by('date')
    else:
        orders= Orders.objects.all().filter(executed__isnull=False ,  expiration__lt=date.today()).order_by('-date')[:20]
    table_orders=TabulatorOrders("table_orders", 'order_view', orders).render()
    return render(request, 'order_list.html', locals())
    
@login_required
def order_view(request, pk):
    order=get_object_or_404(Orders, id=pk)
    return render(request, 'order_view.html', locals())
@login_required
def product_view(request, pk):
    product=get_object_or_404(Products, id=pk)
#    oi=Investmentsoperations.objects.all().filter(investments_id=pk).order_by('datetime')
#    table_io=TabulatorInvestmentsOperations("IO", "investmentoperation_update", oi, investment).render()
#    
#    oic=cursor_rows("select * from investment_operations_current({},now());".format(pk))
#    table_ioc=TabulatorInvestmentsOperationsCurrent("IOC", None, oic, investment).render()
#
#    oih=cursor_rows("select * from investment_operations_historical({},now());".format(pk))
#    table_ioh=TabulatorInvestmentsOperationsHistorical("IOH", None, oih, investment).render()
#
#    dividends=Dividends.objects.all().filter(investments_id=pk).order_by('datetime')
#    list_dividends=tb_queryset(dividends)        
    return render(request, 'product_view.html', locals())
    
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
    concepts= Concepts.objects.all().order_by('name')
    table_conceptos=TabulatorConcepts("table_conceptos", None, concepts).render()
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
def bank_list(request,  active):
    banks= Banks.objects.all().filter(active=active).order_by('name')
    table_banks=TabulatorBanks("table_banks", 'bank_view', banks).render()
    return render(request, 'bank_list.html', locals())
    
def Accounts_listdict(accounts_queryset):    
    
    list_accounts=[]
    for account in accounts_queryset:
        balance=account.balance(timezone.now())
        list_accounts.append({
                "id": account.id, 
                "active":account.active, 
                "name": account.fullName(), 
                "number": account.number,
                "balance": balance[0].string(),  
                "balance_user": balance[1], 
            }
        )
    return list_accounts

@login_required
def account_list(request,  active=True):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    
    accounts= Accounts.objects.all().filter(active=active).order_by('name')
    list_accounts=Accounts_listdict(accounts)
    
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, local_currency).render()
    #balance is aligned left(text) I can do it too with javascript.
    table_accounts=table_accounts.replace(', field:"balance"', ', field:"balance", align:"right"')
    return render(request, 'account_list.html', locals())
        
        
        
@login_required        
def account_view(request, pk, year=date.today().year, month=date.today().month):        
    local_zone=settingsdb("mem/localzone")# perhaps i could acces context??
    account=get_object_or_404(Accounts, pk=pk)
    
    dt_initial=dtaware_month_start(year, month, local_zone)
    accountoperations= Accountsoperations.objects.all().filter(accounts_id=pk, datetime__year=year, datetime__month=month).order_by('datetime')
    table_accountoperations=TabulatorAccountOperations("table_accountoperations", "accountoperation_update", accountoperations, account, dt_initial).render()
  
    creditcards= Creditcards.objects.all().filter(accounts_id=pk, active=True).order_by('name')
    table_creditcards=TabulatorCreditCards("table_creditcards", "bank_update", creditcards, account).render()
  
    return render(request, 'account_view.html', locals())


#@login_required
#def accountoperation_update(request, accounts_id):
#    if request.method == 'POST':
#        form = AccountsoperationsAddForm(request.POST)
#        if form.is_valid():
#            accountoperation=Accountsoperations()
#            accountoperation.comment= form.cleaned_data['comment']
#            accountoperation.concepts=form.cleaned_data['concepts']
#            accountoperation.amount=form.cleaned_data['amount']
#            accountoperation.datetime=form.cleaned_data['datetime']
#            accountoperation.operationstypes=accountoperation.concepts.operationstypes.id
#            accountoperation.accounts=form.cleaned_data['accounts']
#            accountoperation.save()
#            return HttpResponseRedirect( reverse_lazy('account_view', args=(accounts_id,)))
#    else:
#        form = AccountsoperationsAddForm()
#        form.fields['datetime'].widget.attrs['class'] ='form-control datetimepicker-input'
#        form.fields['datetime'].widget.attrs['data-target'] ='#datetimepicker1'
#        form.fields['accounts'].widget = forms.HiddenInput()
##        form.fields['operationstypes'].widget = forms.HiddenInput()
#        form.fields['accounts'].initial=accounts_id
#        form.fields['datetime'].initial=timezone.now()
#    return render(request, 'accountoperation_update.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class accountoperation_update(UpdateView):
    model = Accountsoperations
    fields = ( 'datetime', 'amount', 'concepts',  'accounts', 'comment')
    template_name="accountoperation_update.html"
        

    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(accountoperation_update, self).get_form(form_class)
        form.fields['accounts'].widget = forms.HiddenInput()
        return form
    
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class accountoperation_new(CreateView):
    model = Accountsoperations
    fields = ['datetime', 'concepts', 'amount', 'comment']
    template_name="accountoperation_new.html"
    accounts_id=None

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(accountoperation_new, self).get_form(form_class)
        form.fields['datetime'].initial=timezone.now()
        form.fields['datetime'].widget.attrs['id'] ='datetimepicker'
        return form
        
    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))
  
    def form_valid(self, form):
        form.instance.accounts= Accounts.objects.get(pk=self.kwargs['accounts_id'])
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)


#@login_required
#def accountoperation_new(request, accounts_id):
#    if request.method == 'POST':
#        form = AccountsoperationsAddForm(request.POST)
#        if form.is_valid():
#            accountoperation=Accountsoperations()
#            accountoperation.comment= form.cleaned_data['comment']
#            accountoperation.concepts=form.cleaned_data['concepts']
#            accountoperation.amount=form.cleaned_data['amount']
#            accountoperation.datetime=form.cleaned_data['datetime']
#            accountoperation.operationstypes=form.cleaned_data['concepts'].operationstypes
#            accountoperation.accounts=form.cleaned_data['accounts']
#            accountoperation.save()
#            return HttpResponseRedirect( reverse_lazy('account_view', args=(accounts_id,)))
#    else:
#        form = AccountsoperationsAddForm()
#        form.fields['datetime'].widget.attrs['class'] ='form-control datetimepicker-input'
#        form.fields['datetime'].widget.attrs['data-target'] ='#datetimepicker1'
#        form.fields['accounts'].initial=accounts_id
#        form.fields['accounts'].widget = forms.HiddenInput()
#        form.fields['datetime'].initial=timezone.now()
#    return render(request, 'accountoperation_new.html', {'form': form})

class accountoperation_delete(DeleteView):
    model = Accountsoperations
    template_name = 'accountoperation_delete.html'
    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))

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
    table_io=TabulatorInvestmentsOperations("IO", "investmentoperation_update", oi, investment).render()
    
    oic=cursor_rows("select * from investment_operations_current({},now());".format(pk))
    table_ioc=TabulatorInvestmentsOperationsCurrent("IOC", None, oic, investment).render()

    oih=cursor_rows("select * from investment_operations_historical({},now());".format(pk))
    table_ioh=TabulatorInvestmentsOperationsHistorical("IOH", None, oih, investment).render()

    dividends=Dividends.objects.all().filter(investments_id=pk).order_by('datetime')
    list_dividends=tb_queryset(dividends)        
    return render(request, 'investment_view.html', locals())


@method_decorator(login_required, name='dispatch')
class investmentoperation_new(CreateView):
    model = Investmentsoperations
    fields = ( 'datetime', 'operationstypes',  'shares', 'price',  'taxes',  'commission', 'comment', 'investments', 'currency_conversion')
    template_name="investmentoperation_new.html"
    investments_id=None

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investmentoperation_new, self).get_form(form_class)
        form.fields['datetime'].initial=timezone.now()
        form.fields['currency_conversion'].initial=1
        form.fields['taxes'].initial=0
        form.fields['commission'].initial=0
        form.fields['investments'].widget = forms.HiddenInput()
        return form
        
    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))
  
    def form_valid(self, form):
        form.instance.investments= Investments.objects.get(pk=self.kwargs['investments_id'])
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class investmentoperation_update(UpdateView):
    model = Investmentsoperations
    fields = ( 'datetime', 'operationstypes',  'shares', 'price',  'taxes',  'commission', 'comment', 'investments', 'currency_conversion')
    template_name="investmentoperation_update.html"
        

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investmentoperation_update, self).get_form(form_class)
        form.fields['investments'].widget = forms.HiddenInput()
        return form
    
    def form_valid(self, form):
        return super().form_valid(form)

class investmentoperation_delete(DeleteView):
    model = Investmentsoperations
    template_name = 'investmentoperation_delete.html'
    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))

@login_required
def bank_new(request, pk):
    return render(request, 'bank_new.html', locals())
  
@method_decorator(login_required, name='dispatch')
class bank_update(UpdateView):
    model = Banks
    fields = ['name', 'active']
    template_name="bank_update.html"

    def get_success_url(self):
        return reverse_lazy('bank_list_active')
    
@login_required
def bank_view(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
#    investments= Investments.objects.all().filter(active=active, accounts_id=bank).order_by('name')

    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??


    investments=bank.investments(True)
    table_investments=TabulatorInvestments("table_investments", "investment_view", investments, local_currency).render()
    

    accounts= bank.accounts(True)
    list_accounts=Accounts_listdict(accounts)
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, local_currency).render()
    return render(request, 'bank_view.html', locals())
    

@login_required
def bank_delete(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'bank_delete.html', locals())
