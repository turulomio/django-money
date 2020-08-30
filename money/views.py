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
from django import forms

from money.connection_dj import cursor_rows
from money.forms import SignUpForm, AccountsOperationsForm
from money.models import Banks, Accounts, Accountsoperations, Creditcards,  Investments, Investmentsoperations, Dividends, Concepts, Products,  Orders, Creditcardsoperations
from money.settingsdb import settingsdb
from money.tabulator import  tb_queryset
from money.tables import TabulatorReportConcepts, TabulatorCreditCardsOperations, TabulatorAccountOperations, TabulatorAccounts, TabulatorBanks, TabulatorConcepts, TabulatorCreditCards, TabulatorInvestments, TabulatorInvestmentsOperations, TabulatorInvestmentsOperationsCurrent, TabulatorOrders, TabulatorReportIncomeTotal, TabulatorReportTotal, TabulatorInvestmentsOperationsHistorical
from money.tokens import account_activation_token
from money.reusing.currency import Currency
from money.reusing.datetime_functions import dtaware_month_start, dtaware_month_end
from money.reusing.decorators import timeit
from money.reusing.percentage import Percentage
#from django.utils.translation import ugettext_lazy as _
from money.querysets import qs_accounts_tabulator, qs_banks_tabulator, qs_investments_tabulator, qs_total_report_income_tabulator, qs_total_report_tabulator
from money.otherstuff import total_balance

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
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    banks= Banks.objects.all().filter(active=active).order_by('name')
    banks_list=qs_banks_tabulator(banks, timezone.now(), active, local_currency)
    table_banks=TabulatorBanks("table_banks", 'bank_view', banks_list, local_currency).render()
    return render(request, 'bank_list.html', locals())

@login_required
def account_list(request,  active=True):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    
    accounts= Accounts.objects.all().filter(active=active).order_by('name')
    list_accounts=qs_accounts_tabulator(accounts)
    
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, local_currency).render()
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
    table_creditcards=TabulatorCreditCards("table_creditcards", "creditcard_view", creditcards, account).render()
  
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
class accountoperation_new(CreateView):
    model = Accountsoperations
    template_name="accountoperation_new.html"
    form_class=AccountsOperationsForm

    def get_form(self, form_class=None): 
        form = super(accountoperation_new, self).get_form(form_class)
        form.fields['accounts'].widget = forms.HiddenInput()
        form.fields['accounts'].initial=Accounts.objects.get(pk=self.kwargs['accounts_id'])
        form.fields['datetime'].initial=timezone.now()
        form.fields['datetime'].widget.attrs['id'] ='datetimepicker'
        return form
        
    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))
  
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class accountoperation_update(UpdateView):
    model = Accountsoperations
    template_name="accountoperation_update.html"
    form_class=AccountsOperationsForm

    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))

    def get_form(self, form_class=None): 
        form = super(accountoperation_update, self).get_form(form_class)
        form.fields['accounts'].widget = forms.HiddenInput()
        form.fields['datetime'].widget.attrs['id'] ='datetimepicker'
        return form
    
    def form_valid(self, form):
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
    listdict=qs_investments_tabulator(investments, timezone.now(), local_currency, active)
    table_investments=TabulatorInvestments("table_investments", "investment_view", listdict, local_currency, active).render()

    return render(request, 'investment_list.html', locals())
    
@login_required
def investment_view(request, pk):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    investment=get_object_or_404(Investments, id=pk)
    io, io_current, io_historical=investment.get_investmentsoperations(timezone.now(), local_currency)
   
    table_io=TabulatorInvestmentsOperations("IO", "investmentoperation_update", io, investment).render()
    table_ioc=TabulatorInvestmentsOperationsCurrent("IOC", None, io_current, investment).render()
    table_ioh=TabulatorInvestmentsOperationsHistorical("IOH", None, io_historical, investment).render()

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
class investment_update(UpdateView):
    model = Investments
    fields = ( 'name', 'accounts',  'selling_price', 'products',  'selling_expiration',  'daily_adjustment', 'balance_percentage', 'active')
    template_name="investment_update.html"
        

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.id,))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investment_update, self).get_form(form_class)
        return form
    
    def form_valid(self, form):
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
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??

    investments=bank.investments(True)
    listdic=qs_investments_tabulator(investments, timezone.now(), local_currency, True)
    table_investments=TabulatorInvestments("table_investments", "investment_view", listdic, local_currency, True).render()
    

    accounts= bank.accounts(True)
    list_accounts=qs_accounts_tabulator(accounts)
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, local_currency).render()
    return render(request, 'bank_view.html', locals())
    

@login_required
def bank_delete(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'bank_delete.html', locals())
    
@timeit
@login_required
def report_total(request, year=date.today().year):
    start=timezone.now()
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context?? CRO QUE CON MIDDLEWARE
    local_zone=settingsdb("mem/localzone")# perhaps i could acces context??
    qs_investments=Investments.objects.all()
    qs_accounts=Accounts.objects.all()
    print("Loading querysets took {}".format(timezone.now()-start))
    last_year=dtaware_month_end(year-1, 12, local_zone)
    
    start=timezone.now()
    last_year_balance=total_balance(last_year, local_currency)['total_user']
    str_last_year_balance=Currency(last_year_balance, local_currency).string()
    print("Loading alltotals last_year took {}".format(timezone.now()-start))
    
    start=timezone.now()
    list_report=qs_total_report_tabulator(qs_investments, qs_accounts, year, last_year_balance, local_currency, local_zone)
    table_report_total=TabulatorReportTotal("table_report_total", None, list_report, local_currency).render()
    print("Loading list report took {}".format(timezone.now()-start))
    
    
    start=timezone.now()
    list_report2=qs_total_report_income_tabulator(qs_investments, qs_accounts, year, last_year_balance, local_currency, local_zone)
    table_report_total_income=TabulatorReportIncomeTotal("table_report_total_income", None, list_report2, local_currency).render()
    print("Loading list report income took {}".format(timezone.now()-start))

    return render(request, 'report_total.html', locals())

@login_required
def report_concepts(request, year=date.today().year, month=date.today().month):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context?? CRO QUE CON MIDDLEWARE
    list_report_concepts_positive=[]
    month_balance_positive=0
    dict_month_positive={}
    list_report_concepts_negative=[]
    month_balance_negative=0
    dict_month_negative={}
    dict_median={}
    
    concepts=Concepts.objects.all()   
    
    ## median
    for row in cursor_rows("""
select
    concepts_id as id, 
    median(amount) as median
from 
    accountsoperations
group by 
    concepts_id
"""):
        dict_median[row['id']]=row['median']
    ## Data
    for row in cursor_rows("""
select
    concepts_id as id, 
    sum(amount) as total
from 
    accountsoperations
where 
    date_part('year', datetime)=%s and
    date_part('month', datetime)=%s and
    operationstypes_id in (1,2)
group by 
    concepts_id
""", (year, month)):
        if row['total']>=0:
            month_balance_positive+=row['total']
            dict_month_positive[row['id']]=row['total']
        else:
            month_balance_negative+=row['total']
            dict_month_negative[row['id']]=row['total']

    ## list
    for concept in concepts:
        if concept.id in dict_month_positive.keys():
            list_report_concepts_positive.append({
                "id": concept.id, 
                "name": concept.name, 
                "operationstypes": concept.operationstypes.name, 
                "total": dict_month_positive.get(concept.id, 0), 
                "percentage_total": Percentage(dict_month_positive.get(concept.id, 0), month_balance_positive), 
                "median":dict_median.get(concept.id, 0), 
            })   
    ## list negative
    for concept in concepts:
        if concept.id in dict_month_negative.keys():
            list_report_concepts_negative.append({
                "id": concept.id, 
                "name": concept.name, 
                "operationstypes": concept.operationstypes.name, 
                "total": dict_month_negative.get(concept.id, 0), 
                "percentage_total": Percentage(dict_month_negative.get(concept.id, 0), month_balance_negative), 
                "median":dict_median.get(concept.id, 0), 
            })
    

    table_report_concepts_positive=TabulatorReportConcepts("table_report_concepts_positive", None, list_report_concepts_positive, local_currency).render()
    table_report_concepts_negative=TabulatorReportConcepts("table_report_concepts_negative", None, list_report_concepts_negative, local_currency).render()

    return render(request, 'report_concepts.html', locals())
    
@login_required
def creditcard_view(request, pk):
    local_currency=settingsdb("mem/localcurrency")# perhaps i could acces context??
    creditcard=get_object_or_404(Creditcards, id=pk)
    creditcardoperations=Creditcardsoperations.objects.all().filter(creditcards_id=pk,  paid=False)
    table_creditcardoperations=TabulatorCreditCardsOperations("table_creditcardoperations", 'creditcardoperation_update', creditcardoperations, creditcard).render()

    return render(request, 'creditcard_view.html', locals())
    
class creditcard_delete(DeleteView):
    model = Creditcards
    template_name = 'creditcard_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('creditcard_view',args=(self.object.accounts.id,))
        
        
@method_decorator(login_required, name='dispatch')
class creditcard_new(CreateView):
    model = Creditcards
    template_name="creditcard_new.html"
    fields=("id","name",  "accounts", "number", "maximumbalance", "deferred", "active")

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(creditcard_new, self).get_form(form_class)
        form.fields['accounts'].widget = forms.HiddenInput()
        form.fields['accounts'].initial=Accounts.objects.get(pk=self.kwargs['accounts_id'])
        return form
        
    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))
        
@method_decorator(login_required, name='dispatch')
class creditcard_update(UpdateView):
    model = Creditcards
    template_name="creditcard_update.html"
    fields=("id","name",  "accounts", "number", "maximumbalance", "deferred", "active")


    def get_success_url(self):
        return reverse_lazy('account_view',kwargs={"pk":self.object.accounts.id})

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(creditcard_update, self).get_form(form_class)
        form.fields['accounts'].widget = forms.HiddenInput()
        return form


class creditcardoperation_delete(DeleteView):
    model = Creditcardsoperations
    template_name = 'creditcardoperation_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('creditcard_view',args=(self.object.creditcards.id,))
        
        
@method_decorator(login_required, name='dispatch')
class creditcardoperation_new(CreateView):
    model = Creditcardsoperations
    template_name="creditcardoperation_new.html"
    fields=("id","datetime",  "concepts", "amount", "comment", "creditcards", "paid")

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(creditcardoperation_new, self).get_form(form_class)
        form.fields['creditcards'].widget = forms.HiddenInput()
        form.fields['creditcards'].initial=Creditcards.objects.get(pk=self.kwargs['creditcards_id'])
        form.fields['datetime'].initial=timezone.now()
        form.fields['datetime'].widget.attrs['id'] ='datetimepicker'
        form.fields['paid'].widget = forms.HiddenInput()
        form.fields['paid'].initial=False
        return form
        
    def get_success_url(self):
        return reverse_lazy('creditcard_view',args=(self.object.creditcards.id,))
          
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)
@method_decorator(login_required, name='dispatch')
class creditcardoperation_update(UpdateView):
    model = Creditcardsoperations
    template_name="creditcardoperation_update.html"
    fields=("id","datetime",  "concepts", "amount", "comment", "creditcards", "paid")


    def get_success_url(self):
        return reverse_lazy('creditcard_view',kwargs={"pk":self.object.creditcards.id})

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(creditcardoperation_update, self).get_form(form_class)
        form.fields['creditcards'].widget = forms.HiddenInput()
        form.fields['paid'].widget = forms.HiddenInput()
        form.fields['datetime'].widget.attrs['id'] ='datetimepicker'
        return form
  
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)
