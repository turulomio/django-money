import asyncio
from datetime import  date, datetime
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import render,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from math import floor

from money.connection_dj import cursor_rows, cursor_one_column, execute
from money.forms import (
    AccountsTransferForm, 
    CreditCardPayForm, 
    ProductsRangeForm, 
)
from money.charts import (
    chart_lines_total, 
    chart_product_quotes_historical, 
)
from money.investmentsoperations import InvestmentsOperations_from_investment, InvestmentsOperationsManager_from_investment_queryset
from money.productrange import ProductRangeManager
from money.tables import (
    TabulatorReportConcepts, 
    TabulatorAccountOperations, 
    TabulatorAccounts, 
    TabulatorBanks, 
    TabulatorConcepts, 
    TabulatorCreditCards, 
    TabulatorProducts, 
    TabulatorOrders, 
    TabulatorReportIncomeTotal, 
    TabulatorReportTotal, 
    TabulatorInvestmentsGainsByProductType, 
    TabulatorInvestmentsOperationsHistoricalHeterogeneus,
    TabulatorProductQuotesMonthPercentages, 
    TabulatorProductQuotesMonthQuotes,  
    TabulatorInvestmentsPairsInvestCalculator,
    table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency
)
from money.reusing.casts import string2list_of_integers
from money.reusing.currency import Currency
from money.reusing.datetime_functions import dtaware_month_start, dtaware_month_end, dtaware_changes_tz, epochmicros2dtaware, dtaware2epochmicros
from money.reusing.decorators import timeit
from money.reusing.listdict_functions import listdict_sum, listdict_sum_negatives, listdict_sum_positives, listdict_has_key
from money.reusing.percentage import Percentage
from django.utils.translation import ugettext_lazy as _
from money.listdict import (
    LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount, 
    LdoProductsPairsMonthHistoricalEvolution, 
    LdoInvestmentsRanking, 
    LdoAssetsEvolution, 
    LdoAssetsEvolutionInvested, 
    listdict_accounts, 
    listdict_banks, 
    listdict_chart_total_async, 
    listdict_chart_total_threadpool, 
    listdict_chart_product_quotes_historical, 
    listdict_report_total_income, 
    listdict_report_total,     
    listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month, 
    listdict_accountsoperations_from_queryset, 
    listdict_investments_gains_by_product_type, 
    listdict_investmentsoperationshistorical, 
    listdict_orders, 
    listdict_product_quotes_month_comparation, 
    LdoProductsPairsEvolution, 
    QsoAccountsOperationsHeterogeneus, 
    QsoCreditcardsoperationsHomogeneus, 
    QsoDividendsHomogeneus, 
    QsoDividendsHeterogeneus, 
    QsoInvestments, 
    QsoQuotes, 
    QsoStrategies, 
)
from money.models import (
    Operationstypes, 
    Banks, 
    Accounts, 
    Accountsoperations, 
    Comment, 
    Creditcards,  
    Creditcardsoperations, 
    Investments, 
    Investmentsoperations, 
    Dividends, 
    Concepts, 
    Products,  
    Quotes, 
    Orders, 
    Strategies,  
    StrategiesTypes, 
    total_balance, 
    money_convert, 
)
from xulpymoney.libxulpymoneytypes import eConcept, eComment, eProductType, eOperationType

@login_required
@transaction.atomic
def order_execute(request, pk):
    order=get_object_or_404(Orders, id=pk)
    order.executed=timezone.now()
    order.save()
    order.investments.active=True
    order.investments.save()
    return HttpResponseRedirect(f"{reverse('investmentoperation_new', args=(order.investments.id, ))}?shares={order.shares}&price={order.price}")

## @param year Only used when active=false
@login_required
def order_list(request,  active, year=date.today().year):
    year_start=1970
    year_end=date.today().year
    
    if active is True:
        qs_orders=Orders.objects.all().select_related("investments").select_related("investments__accounts").select_related("investments__products").select_related("investments__products__productstypes").select_related("investments__products").select_related("investments__products__leverages").filter(expiration__gte=datetime.today(), executed=None)
    else:
        qs_orders=Orders.objects.all().select_related("investments").select_related("investments__accounts").select_related("investments__products").select_related("investments__products__productstypes").select_related("investments__products").select_related("investments__products__leverages").filter(Q(date__year=year),  Q(executed__isnull=False) | Q(expiration__lt=datetime.today())).order_by('date')

    ld=listdict_orders(qs_orders)
    table_orders=TabulatorOrders("table_orders", 'order_update', ld, request.local_currency).render()
    return render(request, 'order_list.html', locals())

    
@login_required
def  table_product_list_from_ids(request, ids):
        ids=tuple(ids)
        listproducts=cursor_rows("""
select 
    products.id, 
    products.id as code,
    name, 
    isin, 
    last_datetime, 
    last, 
    percentage(penultimate, last) as percentage_day, 
    percentage(t.lastyear, last) as percentage_year, 
    (select estimation from estimations_dps where year=extract(year from now()) and id=products.id)/last*100 as percentage_dps
from 
    products, 
    last_penultimate_lastyear(products.id,now()) as t
where 
    t.id=products.id and
    products.id in %s""", (ids, ))
        return TabulatorProducts("table_products", 'product_view', listproducts, request.local_currency, request.local_zone )

@login_required
def product_list_search(request):
    search = request.GET.get('search')
    if search!=None:
        searchtitle=_("Searching products that contain '{}' in database").format(search)
        ids=cursor_one_column("""
select 
    products.id
from 
    products
where 
    (name ilike %s or 
     isin ilike %s or
    tickers::text ilike %s)""", [f"%%{search}%%"]*3) 
        table_products=table_product_list_from_ids(request, ids).render()
    return render(request, 'product_list_search.html', locals())
    
@login_required
def product_list_favorites(request):
    favorites=request.globals["mem__favorites"]
    title=_("Favorites product list")
    ids=[]
    for id in favorites.split(","):
        ids.append(int(id))
    table_products=table_product_list_from_ids(request, ids).render()
    return render(request, 'product_list.html', locals())

@login_required
def product_list_indexes(request):
    title=_("Indexes product list")        
    ids=cursor_one_column("""
select 
    products.id
from 
    products
where   
    productstypes_id=%s""", (eProductType.Index, )) 
    table_products=table_product_list_from_ids(request, ids).render()
    return render(request, 'product_list.html', locals())
    
@login_required
def product_list_cfds(request):
    title=_("CFD product list")        
    ids=cursor_one_column("""
select 
    products.id
from 
    products
where   
    productstypes_id in (%s,%s)""", (eProductType.CFD, eProductType.Future)) 
    table_products=table_product_list_from_ids(request, ids).render()
    return render(request, 'product_list.html', locals())

@login_required
def product_benchmark(request):
    return product_view(request, request.globals["mem__benchmarkid"])

@timeit
@login_required
def product_view(request, pk):
    product=get_object_or_404(Products, id=pk)
    quotes, percentages=listdict_product_quotes_month_comparation(2000, product)
    table_quotes_month_percentages=TabulatorProductQuotesMonthPercentages("table_quotes_month_percentages", None, percentages).render()

    table_quotes_month_quotes=TabulatorProductQuotesMonthQuotes("table_quotes_month_quotes", None, quotes, product.currency).render()

    return render(request, 'product_view.html', locals())
    
@timeit
@login_required
def product_ranges(request):
    if request.method == 'POST':
        form = ProductsRangeForm(request.POST)
        if form.is_valid():
            prm=ProductRangeManager(request, form.cleaned_data['products'], form.cleaned_data['percentage_between_ranges'], form.cleaned_data['percentage_gains'], form.cleaned_data['only_first'], form.cleaned_data["accounts"])
            prm.setInvestRecomendation(form.cleaned_data['recomendation_methods'])
            return render(request, 'product_ranges.html', locals())
    else:
        form = ProductsRangeForm()
        product=Products.objects.get(pk=int(request.GET.get("product", request.globals['wdgProductRange__product'])))
        form.fields["products"].initial=product
        form.fields["only_first"].initial=bool(int(request.GET.get("onlyfirst", 0)))
        form.fields['percentage_between_ranges'].initial=Decimal(request.GET.get("percentagebetween", "2500"))/1000
        form.fields['percentage_gains'].initial=Decimal(request.GET.get("percentagegains", "2500"))/1000
        form.fields['amount_to_invest'].initial=request.GET.get("amount", 10000)
        form.fields["recomendation_methods"].initial=request.GET.get("method", 0)
        form.fields["accounts"].initial=request.GET.get("account", None)
    return render(request, 'product_ranges.html', locals())

    
@login_required
def product_update(request):
    data = {}
    if "GET" == request.method:
        return render(request, "product_update.html", data)
    # if not GET, then proceed
    if "csv_file1" not in request.FILES:
        messages.error(request, _('You must upload a file'))
        return HttpResponseRedirect(reverse("product_update"))
    else:
        csv_file = request.FILES["csv_file1"]
        
    if not csv_file.name.endswith('.csv'):
        messages.error(request, _('File is not CSV type'))
        return HttpResponseRedirect(reverse("product_update"))

    #if file is too large, return
    if csv_file.multiple_chunks():
        messages.error(request, _("Uploaded file is too big ({} MB)." ).format(csv_file.size/(1000*1000),))
        return HttpResponseRedirect(reverse("product_update"))

    from money.investing_com import InvestingCom
    InvestingCom(request, csv_file, product=None)
    return HttpResponseRedirect(reverse("product_update"))




@login_required
def concept_list(request):
    concepts= Concepts.objects.all().select_related("operationstypes").order_by('name')
    table_conceptos=TabulatorConcepts("table_conceptos", None, concepts).render()
    return render(request, 'concept_list.html', locals())

def error_403(request, exception):
        data = {}
        return render(request,'403.html', data)

## @todo Add search to search field to repeat search
## @todo Limit search minimum 3 and maximum 50
## @todo Add a tab Widget, author, books, valorations with number in ttab
@timeit
def home(request):
    return render(request, 'home.html', locals())

@login_required
def bank_list(request,  active):
    banks= Banks.objects.all().filter(active=active).order_by('name')
    banks_list=listdict_banks(request, banks, timezone.now(), active)
    table_banks=TabulatorBanks("table_banks", 'bank_view', banks_list, request.local_currency).render()
    return render(request, 'bank_list.html', locals())

@login_required
def account_list(request,  active=True):    
    accounts= Accounts.objects.all().select_related("banks").filter(active=active).order_by('name')
    list_accounts=listdict_accounts(accounts, request.local_currency)
    
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, request.local_currency).render()
    table_accounts=table_accounts.replace(', field:"balance"', ', field:"balance", align:"right"')
    return render(request, 'account_list.html', locals())
        
        
@method_decorator(login_required, name='dispatch')
class account_new(SuccessMessageMixin, CreateView):
    model = Accounts
    fields = ( 'name', 'active', 'number',  'currency')
    template_name="account_new.html"

    def get_success_message(self, cleaned_data):
        return _("Account created successfully")

    def get_success_url(self):
        return reverse_lazy('account_list_active')    
        
    def form_valid(self, form):
        form.instance.banks=Banks.objects.get(pk=self.kwargs['banks_id'])
        form.instance.save()
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class account_update(SuccessMessageMixin, UpdateView):
    model = Accounts
    fields = ( 'name', 'active', 'number',  'currency')
    template_name="account_update.html"

    def get_success_message(self, cleaned_data):
        return _("Account updated successfully")

    def get_success_url(self):
        return reverse_lazy('account_list_active')

@method_decorator(login_required, name='dispatch')
class account_delete(DeleteView):
    model = Accounts
    template_name = 'account_delete.html'
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Account was successfully deleted"))
        return super(DeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('account_list_active')

@login_required        
def account_view(request, pk, year=date.today().year, month=date.today().month): 
    year_start=1970
    year_end=date.today().year + 10
    
    account=get_object_or_404(Accounts, pk=pk)
    
    dt_initial=dtaware_month_start(year, month, request.local_zone)
    initial_balance=float(account.balance( dt_initial, request.local_currency)[0].amount)
    qsaccountoperations= Accountsoperations.objects.all().select_related("concepts").filter(accounts_id=pk, datetime__year=year, datetime__month=month).order_by('datetime')
    listdic_accountsoperations=listdict_accountsoperations_from_queryset(qsaccountoperations, initial_balance)
    table_accountoperations=TabulatorAccountOperations("table_accountoperations", "accountoperation_update", listdic_accountsoperations, account.currency, request.local_zone).render()
    
    #Creditcards
    creditcards=cursor_rows("""
        select 
            id, 
            name, 
            coalesce(sum,0) balance, 
            number, 
            deferred, 
            maximumbalance 
        from 
            creditcards left join  (select creditcards_id, sum(amount) sum from creditcardsoperations where paid is False group by creditcards_id) as t on t.creditcards_id=creditcards.id 
        where 
            active is true and
            accounts_id=%s""", (account.id, ))
    table_creditcards=TabulatorCreditCards("table_creditcards", "creditcard_view", creditcards, account).render()
  
    return render(request, 'account_view.html', locals())        
        
@login_required       
@transaction.atomic
def account_transfer(request, origin): 
    origin=get_object_or_404(Accounts, pk=origin)
    if request.method == 'POST':
        form = AccountsTransferForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['commission']>0:
                ao_commission=Accountsoperations()
                ao_commission.datetime=form.cleaned_data['datetime']
                concept_commision=Concepts.objects.get(pk=eConcept.BankCommissions)
                ao_commission.concepts=concept_commision
                ao_commission.operationstypes=concept_commision.operationstypes
                ao_commission.amount=-form.cleaned_data['commission']
                ao_commission.accounts=origin
                ao_commission.save()
            else:
                ao_commission=None

            #Origin
            ao_origin=Accountsoperations()
            ao_origin.datetime=form.cleaned_data['datetime']
            concept_transfer_origin=Concepts.objects.get(pk=eConcept.TransferOrigin)
            ao_origin.concepts=concept_transfer_origin
            ao_origin.operationstypes=concept_transfer_origin.operationstypes
            ao_origin.amount=-form.cleaned_data['amount']
            ao_origin.accounts=origin
            ao_origin.save()

            #Destiny
            ao_destiny=Accountsoperations()
            ao_destiny.datetime=form.cleaned_data['datetime']
            concept_transfer_destiny=Concepts.objects.get(pk=eConcept.TransferDestiny)
            ao_destiny.concepts=concept_transfer_destiny
            ao_destiny.operationstypes=concept_transfer_destiny.operationstypes
            ao_destiny.amount=form.cleaned_data['amount']
            ao_destiny.accounts=form.cleaned_data['destiny']
            ao_destiny.save()

            #Encoding comments
            ao_origin.comment=Comment().encode(eComment.AccountTransferOrigin, ao_origin, ao_destiny, ao_commission)
            ao_origin.save()
            ao_destiny.comment=Comment().encode(eComment.AccountTransferDestiny, ao_origin, ao_destiny, ao_commission)
            ao_destiny.save()
            if ao_commission is not None:
                ao_commission.comment=Comment().encode(eComment.AccountTransferOriginCommission, ao_origin, ao_destiny, ao_commission)
                ao_commission.save()

            return HttpResponseRedirect( reverse_lazy('account_view', args=(origin.id,)))
    else:
        form = AccountsTransferForm()
        widget_datetime(request, form.fields['datetime'])
        form.fields['datetime'].initial=str(dtaware_changes_tz(timezone.now(), request.local_zone))
        form.fields['commission'].initial=0
  
    return render(request, 'account_transfer.html', locals())

@login_required       
@transaction.atomic
def account_transfer_delete(request, comment): 
    decode_objects=Comment().decode_objects(comment)
    if request.method == 'POST':
        decode_objects["origin"].delete()
        decode_objects['destiny'].delete()
        if decode_objects['commission'] is not None:
            decode_objects['commission'].delete()
        return HttpResponseRedirect( reverse_lazy('account_view', args=(decode_objects['origin'].accounts.id,)))

    return render(request, 'account_transfer_delete.html', locals())

@method_decorator(login_required, name='dispatch')
class accountoperation_new(CreateView):
    model = Accountsoperations
    template_name="accountoperation_new.html"
    
    fields = ( 'datetime', 'concepts', 'amount',  'comment')

    def get_form(self, form_class=None): 
        form = super(accountoperation_new, self).get_form(form_class)
        widget_datetime(self.request, form.fields['datetime'])
        form.fields['concepts'].queryset=Concepts.queryset_for_accountsoperations_order_by_fullname()
        return form
        
    def get_initial(self):
        d={}
        if self.kwargs['dt']==0:
            dt_=dtaware_changes_tz(timezone.now(), self.request.local_zone)
        else:
            dt_=dtaware_changes_tz(epochmicros2dtaware(self.kwargs['dt']), self.request.local_zone)
        d["datetime"]= str(dt_)
        if self.kwargs['concepts_id']!=0:
            d["concepts"]=Concepts.objects.get(pk=self.kwargs['concepts_id'])

        account=Accounts.objects.get(pk=self.kwargs['accounts_id'])
        initial_balance=float(account.balance( dtaware_month_start(dt_.year, dt_.month, self.request.local_zone), self.request.local_currency)[0].amount)
        qsaccountoperations= Accountsoperations.objects.all().select_related("concepts").filter(accounts_id=account.id, datetime__year=dt_.year,  datetime__month=dt_.month).order_by('datetime')
        listdic_accountsoperations=listdict_accountsoperations_from_queryset(qsaccountoperations, initial_balance)
        self.table_accountoperations=TabulatorAccountOperations("table_accountoperations", "accountoperation_update", listdic_accountsoperations, account.currency, self.request.local_zone).render()

        return d
    
    def get_success_url(self):
        return reverse_lazy('accountoperation_new',args=(self.object.accounts.id, dtaware2epochmicros(self.object.datetime)+1000000,  self.object.concepts.id))
  
    def form_valid(self, form):
        if  (
                (form.instance.concepts.operationstypes.id==eOperationType.Income and form.instance.amount>=0) or
                (form.instance.concepts.operationstypes.id==eOperationType.Expense and form.instance.amount <0) or
                (form.instance.concepts.operationstypes.id==eOperationType.DerivativeManagement)
            ):
            form.instance.accounts=Accounts.objects.get(pk=self.kwargs['accounts_id'])
            form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes    
            return super().form_valid(form)
        else:
            if form.instance.concepts.operationstypes.id==eOperationType.Expense and form.instance.amount>=0:
                    form.add_error(None, ValidationError(_('Amount must be negative')))
            if form.instance.concepts.operationstypes.id==eOperationType.Income and form.instance.amount<=0:
                    form.add_error(None, ValidationError(_('Amount must be positive')))
            return super().form_invalid(form)



@login_required
def accountoperation_search(request):
    search = request.GET.get('search')
    if search is not None:
        searchtitle=_(f"Searching accounts operations that contain '{search}'")
        qso_ao=QsoAccountsOperationsHeterogeneus(
            request,  
            Accountsoperations.objects.all().select_related("concepts").select_related("accounts").select_related("accounts__banks").filter(comment__icontains=search).order_by('datetime')
        )
    strsearch="" if search is None else search
    return render(request, 'accountoperation_search.html', locals())

@method_decorator(login_required, name='dispatch')
class accountoperation_update(UpdateView):
    model = Accountsoperations
    template_name="accountoperation_update.html"
    fields = ( 'datetime', 'concepts', 'amount',  'comment')

    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))

    def get_form(self, form_class=None): 
        form = super(accountoperation_update, self).get_form(form_class)
        widget_datetime(self.request, form.fields['datetime'])
        form.fields['concepts'].queryset=Concepts.queryset_for_accountsoperations_order_by_fullname()
            
        ## Gets the investment operation for io account ooperations only for that
        if self.object.is_investmentoperation() is True:
            self.io=Comment().decode_objects(self.object.comment)        
        return form
        
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(self.object.datetime, self.request.local_zone)), 
        }
        
    def form_valid(self, form):
        if  (
                (form.instance.concepts.operationstypes.id==eOperationType.Income and form.instance.amount>=0) or
                (form.instance.concepts.operationstypes.id==eOperationType.Expense and form.instance.amount <0) or
                (form.instance.concepts.operationstypes.id==eOperationType.DerivativeManagement)
            ):
            form.instance.accounts=Accountsoperations.objects.get(pk=self.kwargs['pk']).accounts
            form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
            return super().form_valid(form)
        else:
            if form.instance.concepts.operationstypes.id==eOperationType.Expense and form.instance.amount>=0:
                    form.add_error(None, ValidationError(_('Amount must be negative')))
            if form.instance.concepts.operationstypes.id==eOperationType.Income and form.instance.amount<=0:
                    form.add_error(None, ValidationError(_('Amount must be positive')))
            return super().form_invalid(form)

class accountoperation_delete(DeleteView):
    model = Accountsoperations
    template_name = 'accountoperation_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))

@login_required
def investment_list(request,  active):
    investments= Investments.objects.all().select_related('accounts').select_related('products').select_related("products__productstypes").select_related("products__leverages").filter(active=active)
    qso=QsoInvestments(request, investments)

    if active is True:
        listdict=qso.listdict_active()
        table=qso.tabulator_active()
    else:
        listdict=qso.listdict_inactive()
        table=qso.tabulator_inactive()
    # Foot only for active investments
    if listdict_has_key(listdict, "gains") is True:
        positives=Currency(listdict_sum_positives(listdict, "gains"), request.local_currency)
        negatives=Currency(listdict_sum_negatives(listdict, "gains"), request.local_currency)
        foot=_(f"Positive gains - Negative gains = {positives} {negatives} = {positives+negatives}")
        balance_futures=_(f"Investments balance with futures is {Currency(qso.iotm.current_balance_futures_user(), request.local_currency)}")

    return render(request, 'investment_list.html', locals())
    
@timeit
@login_required
def investment_pairs(request, worse, better, accounts_id):
    #Dastabase
    product_better=Products.objects.all().filter(id=better)[0]
    product_worse=Products.objects.all().filter(id=worse)[0]
    d_product_better=Products.get_d_product_with_basics(better)
    d_product_worse=Products.get_d_product_with_basics(worse)
    basic_results_better=product_better.basic_results()
    basic_results_worse=product_worse.basic_results()
    dict_ot=Operationstypes.dictionary()
    account=Accounts.objects.all().filter(id=accounts_id)[0]
    
    #Variables
    ldo_ioc_better=LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount(request, "ldo_better")
    ldo_ioc_better.set_from_db_and_variables(d_product_better, account)
    ldo_ioc_worse=LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount(request, "ldo_worse")
    ldo_ioc_worse.set_from_db_and_variables(d_product_worse, account)
    
    table_ioc_better_usercurrency=table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency(ldo_ioc_better.ld,  request.local_zone, "table_ioc_better_usercurrency")
    table_ioc_worse_usercurrency=table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency(ldo_ioc_worse.ld,  request.local_zone, "table_ioc_worse_usercurrency")

    pair_invested=ldo_ioc_better.invested()+ldo_ioc_worse.invested()
    pair_gains=Currency(ldo_ioc_better.sum('gains_net_user')+ldo_ioc_worse.sum('gains_net_user'), request.local_currency)
    balance_deviation =ldo_ioc_better.balance_cfd()-ldo_ioc_worse.balance_cfd()
    max_deviation=Currency(pair_invested*Decimal(0.10),  request.local_currency)

    ldo_products_evolution=LdoProductsPairsEvolution(request,"LdoProductsPairsEvolution")
    ldo_products_evolution.set_from_db_and_variables(product_worse, product_better, ldo_ioc_worse.ld, ldo_ioc_better.ld, basic_results_worse,  basic_results_better)
    
    #Variables to calculate reinvest loses
    gains=ldo_ioc_better.sum("gains_gross_user")+ldo_ioc_worse.sum("gains_gross_user")
    return render(request, 'investment_pairs.html', locals())

@login_required
def products_pairs(request, worse, better):
    product_better=get_object_or_404(Products, pk=better)
    product_worse=get_object_or_404(Products, pk=worse)
    
    fromyear=date.today().year-3 if request.GET.get("fromyear", None) is None else request.GET["fromyear"]
    ldo=LdoProductsPairsMonthHistoricalEvolution(request, product_worse, product_better)
        
    return render(request, 'products_pairs.html', locals())


@login_required
def ajax_investment_pairs_invest(request, worse, better, accounts_id, amount ):
    product_better=Products.objects.all().filter(id=better)[0]
    product_worse=Products.objects.all().filter(id=worse)[0]
    d_product_better=Products.get_d_product_with_basics(better)
    d_product_worse=Products.get_d_product_with_basics(worse)
    account=Accounts.objects.all().filter(id=accounts_id)[0]    
    list_ioc_better=LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount(request,  name="ldo2_better")
    list_ioc_better.set_from_db_and_variables(d_product_better, account)
    list_ioc_worse=LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount( request,  name="ldo2_worse")
    list_ioc_worse.set_from_db_and_variables(d_product_worse, account)

    listdict=[]
    last_user=money_convert(timezone.now(), d_product_better['last'], product_better.currency, request.local_currency)# last in user currency
    better_current_user=list_ioc_better.shares()*product_better.real_leveraged_multiplier()*last_user
    better_new_shares=round(amount/last_user/product_better.real_leveraged_multiplier(), 2)
    better_invested=listdict_sum(list_ioc_better.ld, "invested_user")
    better_new= better_new_shares*last_user*product_better.real_leveraged_multiplier()
    better_total=better_current_user+better_new
    listdict.append({   
        'name': product_better.name, 
        'last_datetime': d_product_better["last_datetime"], 
        'last': d_product_better["last"], 
        'invested': better_invested, 
        'current': better_current_user, 
        'new': better_new, 
        'new_plus_current': better_total, 
        'shares': better_new_shares, 
      })    
    
    worse_invested=abs(listdict_sum(list_ioc_worse.ld, "invested_user"))
    worse_current=worse_invested+listdict_sum(list_ioc_worse.ld, "gains_gross_user")
    worse_new_shares=Decimal(floor((better_total-worse_current)/d_product_worse["last"]/product_worse.real_leveraged_multiplier()/Decimal(0.01))*Decimal(0.01))#Sifnificance
    worse_new= worse_new_shares*d_product_worse["last"]*product_worse.real_leveraged_multiplier()
    worse_total=worse_current+worse_new
    listdict.append({   
        'name': product_worse.name, 
        'last_datetime': d_product_worse["last_datetime"], 
        'last': d_product_worse["last"], 
        'invested': worse_invested, 
        'current': worse_current, 
        'new': worse_new, 
        'new_plus_current': worse_total, 
        'shares': worse_new_shares, 
      })
    table_calculator=TabulatorInvestmentsPairsInvestCalculator("table_calculator", None, listdict, request.local_currency, request.local_zone).render()
    return HttpResponse(table_calculator)


@login_required
def investment_view(request, pk):
    investment=get_object_or_404(Investments.objects.select_related("accounts").select_related("products").select_related("products__productstypes"), id=pk)
    operations=investment.operations(request, request.local_currency)
    
    qso_dividends=QsoDividendsHomogeneus(request,  Dividends.objects.all().filter(investments_id=pk).order_by('datetime'),  investment)
    return render(request, 'investment_view.html', locals())

@method_decorator(login_required, name='dispatch')
class investmentoperation_new(CreateView):
    model = Investmentsoperations
    fields = ( 'datetime', 'operationstypes',  'shares', 'price',  'taxes',  'commission', 'comment', 'currency_conversion')
    template_name="investmentoperation_new.html"

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()

        self.investments=Investments.objects.select_related("accounts").select_related("products").select_related("products__productstypes").select_related("products__leverages").get(pk=self.kwargs['investments_id']) #We can use in template with view.investments
        form = super(investmentoperation_new, self).get_form(form_class)
        widget_datetime(self.request, form.fields['datetime'])
        widget_currency_conversion(self.request, form.fields['currency_conversion'], self.investments.accounts.currency, self.investments.products.currency)
        form.fields['operationstypes'].queryset=Operationstypes.objects.filter(pk__in=[4, 5, 6])
        return form
                
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.local_zone)), 
            'currency_conversion': str(self.request.GET.get("currency_conversion", 1)), 
            'shares': self.request.GET.get("shares", 0), 
            'price': self.request.GET.get("price", 0), 
            'taxes':0, 
            'commission':0, 
            }

    def get_success_url(self):
        return reverse_lazy('investment_view', args=(self.object.investments.id,))

    @transaction.atomic
    def form_valid(self, form):
        form.instance.investments=Investments.objects.select_related("products").select_related("products__productstypes").select_related("products__leverages").get(pk=self.kwargs['investments_id']) #We can use in template with view.investments
        if (    form.instance.commission>=0 and 
                form.instance.taxes>=0 and 
                ((form.instance.shares>=0 and form.instance.operationstypes.id in (4, 6)) or (form.instance.shares<0 and form.instance.operationstypes.id==5) )) :
            form.instance.save()
            form.instance.update_associated_account_operation(self.request, self.request.local_currency)
            return super().form_valid(form)
        else:
            if form.instance.commission<0:
                form.add_error(None, ValidationError({"commission": "Commission must be positive ..."}))    
            if form.instance.taxes<0:
                form.add_error(None, ValidationError({"taxes": "Taxes must be positive ..."}))    
            if form.instance.shares<0 and form.instance.operationstypes.id in (4, 6):
                form.add_error(None, ValidationError({"shares": "Shares can't be negative for this operation type..."}))    
            if form.instance.shares>0 and form.instance.operationstypes.id in (5, ):
                form.add_error(None, ValidationError({"shares": "Shares can't be positive for this operation type..."}))    
            return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class investmentoperation_update(UpdateView):
    model = Investmentsoperations
    fields = ( 'datetime', 'investments',  'operationstypes',  'shares', 'price',  'taxes',  'commission', 'comment', 'currency_conversion')
    template_name="investmentoperation_update.html"
        
    def get_success_url(self):
        if self.request.GET.get("next", None) is not None:
            return self.request.GET.get("next")
        return reverse_lazy('investment_view',args=(self.object.investments.id,))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investmentoperation_update, self).get_form(form_class) 
        widget_datetime(self.request, form.fields['datetime'])
        widget_currency_conversion(self.request, form.fields['currency_conversion'], self.object.investments.accounts.currency, self.object.investments.products.currency)
        form.fields['operationstypes'].queryset=Operationstypes.objects.filter(pk__in=[4, 5, 6])
        
        form.fields['investments'].queryset=Investments.queryset_for_investments_products_combos_order_by_fullname()
        return form

    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(self.object.datetime, self.request.local_zone)), 
            }

    @transaction.atomic
    def form_valid(self, form):
        if (    form.instance.commission>=0 and 
                form.instance.taxes>=0 and 
                ((form.instance.shares>=0 and form.instance.operationstypes.id in (4, 6)) or (form.instance.shares<0 and form.instance.operationstypes.id==5) )) :
            form.instance.save()
            form.instance.update_associated_account_operation(self.request, self.request.local_currency)
            return super().form_valid(form)
        else:
            if form.instance.commission<0:
                form.add_error(None, ValidationError({"commission": "Commission must be positive ..."}))    
            if form.instance.taxes<0:
                form.add_error(None, ValidationError({"taxes": "Taxes must be positive ..."}))    
            if form.instance.shares<0 and form.instance.operationstypes.id in (4, 6):
                form.add_error(None, ValidationError({"shares": "Shares can't be negative for this operation type..."}))    
            if form.instance.shares>0 and form.instance.operationstypes.id in (5, ):
                form.add_error(None, ValidationError({"shares": "Shares can't be positive for this operation type..."}))    
            return super().form_invalid(form)

class investmentoperation_delete(DeleteView):
    model = Investmentsoperations
    template_name = 'investmentoperation_delete.html'
    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))   
       
    @transaction.atomic
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        execute("delete from investmentsaccountsoperations where investmentsoperations_id=%s",(self.object.id, )) 
        return super(investmentoperation_delete, self).delete(*args, **kwargs)


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

    investments=bank.investments(True)
    qso_investments=QsoInvestments(request, investments)
    accounts= bank.accounts(True)
    list_accounts=listdict_accounts(accounts, request.local_currency)
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, request.local_currency).render()
    return render(request, 'bank_view.html', locals())
    

@login_required
def bank_delete(request, pk):
    bank=get_object_or_404(Banks, pk=pk)
    return render(request, 'bank_delete.html', locals())
    
@timeit
@login_required
def report_total(request, year=date.today().year):
    year_start=1970
    year_end=date.today().year + 10
    last_year=dtaware_month_end(year-1, 12, request.local_zone)
    
    start=timezone.now()
    last_year_balance=Currency(total_balance(last_year, request.local_currency)['total_user'], request.local_currency)
    print("Loading alltotals last_year took {}".format(timezone.now()-start))
    
    start=timezone.now()
    list_report=listdict_report_total(year, last_year_balance, request.local_currency, request.local_zone)
    table_report_total=TabulatorReportTotal("table_report_total", None, list_report, request.local_currency).render()
    print("Loading list report took {}".format(timezone.now()-start))
    
    return render(request, 'report_total.html', locals())
    
@timeit
@login_required
def report_evolution(request):
    from_year=date.today().year-3 if request.GET.get("from_year", None) is None else int(request.GET["from_year"])

    ldo_assets=LdoAssetsEvolution(request,  from_year)
    ldo_invested=LdoAssetsEvolutionInvested(request, from_year)
    
    return render(request, 'report_evolution.html', locals())



@timeit
@login_required
def ajax_chart_total(request, year_from):
    year_start=1970
    year_end=date.today().year + 10
    ld_chart_total=listdict_chart_total_threadpool(year_from, request.local_currency, request.local_zone)
    chart_total=chart_lines_total(ld_chart_total, request.local_currency)
    return render(request, 'chart_total.html', locals())

@login_required
def ajax_chart_total_async(request, year_from):
    year_start=1970
    year_end=date.today().year + 10
    start=datetime.now()
    ld_chart_total=asyncio.run(listdict_chart_total_async(year_from, request.local_currency, request.local_zone))
    print(f"listdict_chart_total_async took {datetime.now()-start}")
    chart_total=chart_lines_total(ld_chart_total, request.local_currency)
    return render(request, 'chart_total.html', locals())


@timeit
@login_required
def ajax_investment_to_json(request, pk):
    investment=get_object_or_404(Investments.objects.select_related("products").select_related("products__leverages"), id=pk)
    result = { 'leverages': investment.products.real_leveraged_multiplier(), 
           'decimals': investment.products.decimals,
           'currency': investment.products.currency, 
         }
    return JsonResponse(result)

@timeit
@login_required
def ajax_chart_product_quotes_historical(request, pk):
    product=get_object_or_404(Products, id=pk)
    ld_chart_total=listdict_chart_product_quotes_historical(None, product, request.local_currency, request.local_zone)
    chart_total=chart_product_quotes_historical(ld_chart_total, request.local_currency)
    return HttpResponse(chart_total)

@timeit
@login_required
def ajax_report_total_income(request, year=date.today().year):  
    qs_investments=Investments.objects.all()
    list_report2=listdict_report_total_income(request, qs_investments, year, request.local_currency, request.local_zone)
    table_report_total_income=TabulatorReportIncomeTotal("table_report_total_income", "report_total_income_details", list_report2, request.local_currency).render()
    return HttpResponse(table_report_total_income)

@timeit
@login_required
def ajax_report_gains_by_product_type(request, year=date.today().year):
    list_report=listdict_investments_gains_by_product_type(year, request.local_currency)
    table_investments_gains_by_product_type=TabulatorInvestmentsGainsByProductType("table_investments_gains_by_product_type", None, list_report, request.local_currency).render()
    gross=Currency(listdict_sum(list_report, "dividends_gross")+ listdict_sum(list_report, "gains_gross"), request.local_currency)
    net=Currency(listdict_sum(list_report, "dividends_net")+ listdict_sum(list_report, "gains_net"), request.local_currency)
    s=f"<p>Gross gains + Gross dividends = {gross.string()}.</p><p>Net gains + Net dividends = {net.string()}.</p>"
    return HttpResponse(table_investments_gains_by_product_type+s)
    

def ajax_modal_button(request):
    return HttpResponse("""<modal-window>
    Dentro modal window
    <p> HOLA </p>
</modal-window>""")

@timeit
@login_required
def report_total_income_details(request, year=date.today().year, month=date.today()):
    expenses=listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month(year, month, 2,  request.local_currency, request.local_zone)
    table_expenses=TabulatorAccountOperations("table_expenses", None, expenses, request.local_currency,  request.local_zone).render()
    incomes=listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month(year, month, 1,  request.local_currency, request.local_zone)
    table_incomes=TabulatorAccountOperations("table_incomes", None, incomes, request.local_currency,  request.local_zone).render()
        
    qso_dividends=QsoDividendsHeterogeneus(request,  Dividends.objects.all().filter(datetime__year=year, datetime__month=month).order_by('datetime'))
    
    gains=listdict_investmentsoperationshistorical(request, year, month, request.local_currency, request.local_zone)
    table_gains=TabulatorInvestmentsOperationsHistoricalHeterogeneus("table_gains", None, gains, request.local_currency, request.local_zone).render()
    return render(request, 'report_total_income_details.html', locals())

        
        
@method_decorator(login_required, name='dispatch')
class quote_new(CreateView):
    model = Quotes
    template_name="quote_new.html"
    fields=("id","datetime",  "quote", "products")

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(quote_new, self).get_form(form_class)
        form.fields['products'].widget = forms.HiddenInput()
        widget_datetime(self.request, form.fields['datetime'])
        return form
        
    def get_context_data(self, **kwargs):
        context = super(quote_new, self).get_context_data(**kwargs)
        context['product'] = self.product
        return context
        
        
    def get_initial(self):
        self.product=Products.objects.get(pk=self.kwargs['products_id'])
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.local_zone)), 
            'products': self.product
        }
        
    def get_success_url(self):
        return reverse_lazy('investment_list_active')
          
    def form_valid(self, form):
        return super().form_valid(form)

@login_required
def quote_delete_last(request, products_id): 
    Quotes.objects.filter(products_id=products_id).latest('datetime').delete();
    if request.GET.get("next", None) is None:
        return HttpResponseRedirect( reverse_lazy('product_view', args=(products_id,)))
    else:
        return HttpResponseRedirect( request.GET.get("next"))
@login_required
def quote_delete(request): 
    try:
        ids=string2list_of_integers(request.GET.get("ids"), separator=",")
        qs=Quotes.objects.filter(pk__in=ids)
        if len(qs)>0:
            qs.delete()
    except:
        print("Error parsing",  request.GET.get("ids"))
        pass
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        
@login_required
def quote_list(request, products_id): 
    product=get_object_or_404(Products, pk=products_id)
    qs=Quotes.objects.select_related("products").filter(products=product).order_by("datetime")
    qso=QsoQuotes(request, qs)  
    return render(request, 'quote_list.html', locals())
        
@method_decorator(login_required, name='dispatch')
class quote_update(SuccessMessageMixin, UpdateView):
    model = Quotes
    fields = ( 'datetime', 'quote',)
    template_name="quote_update.html"

    def get_success_message(self, cleaned_data):
        return _("Quote was updated successfully")

    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(self.object.datetime, self.request.local_zone)), 
        }

    def get_success_url(self):
        return reverse_lazy('quote_list', args=(self.object.products.id, ))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(quote_update, self).get_form(form_class)
        widget_datetime(self.request, form.fields['datetime'])
        return form

@login_required
def report_concepts(request, year=date.today().year, month=date.today().month):
    year_start=1970
    year_end=date.today().year+10
    list_report_concepts_positive=[]
    month_balance_positive=0
    dict_month_positive={}
    list_report_concepts_negative=[]
    month_balance_negative=0
    dict_month_negative={}
    dict_median={}
    
    concepts=Concepts.objects.all().select_related("operationstypes")
    
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
    

    table_report_concepts_positive=TabulatorReportConcepts("table_report_concepts_positive", None, list_report_concepts_positive, request.local_currency).render()
    table_report_concepts_negative=TabulatorReportConcepts("table_report_concepts_negative", None, list_report_concepts_negative, request.local_currency).render()

    return render(request, 'report_concepts.html', locals())

@timeit
@login_required
@transaction.atomic
def creditcard_pay(request, pk):
    creditcard=Creditcards.objects.get(pk=pk)
    qso_creditcardoperations=QsoCreditcardsoperationsHomogeneus(
        request, 
        Creditcardsoperations.objects.all().select_related("concepts").select_related("concepts__operationstypes").filter(creditcards_id=creditcard.id,  paid=False).order_by("datetime"), 
        creditcard, 
        "qso_cco"
    )
    if request.method == 'POST':
        form = CreditCardPayForm(request.POST)
        widget_datetime(request, form.fields['datetime'])
        if form.is_valid():
            messages.success(request, _("Credit card payed."))
            c=Accountsoperations()
            c.datetime=form.cleaned_data['datetime']
            c.concepts=Concepts.objects.get(pk=eConcept.CreditCardBilling)
            c.operationstypes=c.concepts.operationstypes
            c.amount=form.cleaned_data['amount']
            c.accounts=creditcard.accounts
            c.comment="Transaction in progress"
            c.save()
            c.comment=Comment().encode(eComment.CreditCardBilling, creditcard, c)
            c.save()
        
            qs_cco=Creditcardsoperations.objects.all().filter(pk__in=(string2list_of_integers(form.cleaned_data['operations_id'])))
            #Modifica el registro y lo pone como paid y la datetime de pago y añade la opercuenta
            for o in qs_cco:
                o.paid_datetime=form.cleaned_data['datetime']
                o.paid=True
                o.accountsoperations_id=c.id
                o.save()
            return render(request, 'creditcard_pay.html', locals())
    else:
        form = CreditCardPayForm()
        form.fields["datetime"].initial= str(dtaware_changes_tz(timezone.now(), request.local_zone))
        widget_datetime(request, form.fields['datetime'])
        
    return render(request, 'creditcard_pay.html', locals())

@login_required
@transaction.atomic
def creditcard_pay_refund(request, accountsoperations_id):
    ao=get_object_or_404(Accountsoperations, pk=accountsoperations_id)
    d=Comment().decode_objects(ao.comment)
    
    Creditcardsoperations.objects.filter(accountsoperations_id=ao.id).update(paid_datetime=None,  paid=False, accountsoperations_id=None)

    ao.delete() #Must be at the end due to middle queries
    messages.success(request, _("Credit card bill refunded"))
    return HttpResponseRedirect(reverse("creditcard_view", args=(d["creditcard"].id, )))

@login_required
def creditcard_view(request, pk):
    creditcard=get_object_or_404(Creditcards, id=pk)
    qso_creditcardoperations=QsoCreditcardsoperationsHomogeneus(
        request, 
        Creditcardsoperations.objects.all().select_related("concepts").select_related("concepts__operationstypes").filter(creditcards_id=pk,  paid=False).order_by("datetime"), 
        creditcard, 
        "qso_cco"
    )
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
        widget_datetime(self.request, form.fields['datetime'])
        form.fields['concepts'].queryset=Concepts.queryset_for_accountsoperations_order_by_fullname()
        form.fields['paid'].widget = forms.HiddenInput()
        return form
        
                        
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.local_zone)), 
            'paid':False,
            }

        
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
        
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(self.object.datetime, self.request.local_zone)), 
        }
        
    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(creditcardoperation_update, self).get_form(form_class)
        form.fields['creditcards'].widget = forms.HiddenInput()
        form.fields['paid'].widget = forms.HiddenInput()
        widget_datetime(self.request, form.fields['datetime'])
        form.fields['concepts'].queryset=Concepts.queryset_for_accountsoperations_order_by_fullname()
        return form
  
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)
    
@login_required
def strategy_list(request, active=True):
    qs_strategies=Strategies.objects.all().filter(dt_to__isnull=active)
    qso_strategies=QsoStrategies(request, qs_strategies)
    #table_strategies=TabulatorStrategies("table_strategies", "strategy_view", strategies, request.local_currency).render()
    return render(request, 'strategy_list.html', locals())
        

@timeit
@login_required
def strategy_view(request, pk):
    strategy=get_object_or_404(Strategies, pk=pk)
    investments_ids=string2list_of_integers(strategy.investments)
    iom=InvestmentsOperationsManager_from_investment_queryset(
        Investments.objects.select_related("accounts").filter(id__in=(investments_ids)), 
        timezone.now(), 
        request
    )
    
    ops=iom.LdoInvestmentsOperationsHeterogeneus_between(strategy.dt_from, strategy.dt_to_for_comparations())
    current=iom.LdoInvestmentsOperationsCurrentHeterogeneus_between(strategy.dt_from, strategy.dt_to_for_comparations())
    historical=iom.LdoInvestmentsOperationsHistoricalHeterogeneus_between(strategy.dt_from, strategy.dt_to_for_comparations())
    
    qso_dividends=QsoDividendsHeterogeneus(
        request,  
        Dividends.objects.all().filter(investments_id__in=investments_ids, datetime__range=(strategy.dt_from, strategy.dt_to_for_comparations())).order_by('datetime'),  
    )

    return render(request, 'strategy_view.html', locals())

        
@method_decorator(login_required, name='dispatch')
class strategy_new(CreateView):
    model = Strategies
    template_name="strategy_new.html"
    fields = ( 'name','dt_from', 'dt_to', 'investments',  'comment','type',  'additional1',  'additional2',  'additional3',  'additional4', 'additional5', 'additional6', 'additional7', 'additional8', 'additional9', 'additional10')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(strategy_new, self).get_form(form_class)
        form.fields['name'].widget = forms.TextInput()
        widget_datetime(self.request, form.fields['dt_from'])
        widget_datetime(self.request, form.fields['dt_to'])
        return form

    def get_initial(self):
        return {
            'dt_from': str(dtaware_changes_tz(timezone.now(),  self.request.local_zone)), 
        }

    def form_valid(self, form):
        if form.instance.type==StrategiesTypes.PairsInSameAccount:
            if form.instance.additional1 is None or form.instance.additional2 is None or form.instance.additional3 is None:
                form.add_error(None, ValidationError({"type": "Additional 1, 2 and 3 can't be empty"}))                
                return super().form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('strategy_list_active')
        
@method_decorator(login_required, name='dispatch')
class strategy_update(UpdateView):
    model = Strategies
    fields = ( 'name','dt_from', 'dt_to', 'investments',  'comment','type',  'additional1',  'additional2',  'additional3',  'additional4', 'additional5', 'additional6', 'additional7', 'additional8', 'additional9', 'additional10')
    template_name="strategy_update.html"

    def get_success_url(self):
        return reverse_lazy('strategy_list_active')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(strategy_update, self).get_form(form_class)
        form.fields['name'].widget = forms.TextInput()
        widget_datetime(self.request, form.fields['dt_from'])
        widget_datetime(self.request, form.fields['dt_to'])
        return form

    def get_initial(self):
        d={}
        d['dt_from']= str(dtaware_changes_tz(self.object.dt_from, self.request.local_zone))
        
        if self.object.dt_to is None:
            d["dt_to"]= ""
        else:
            d['dt_to']=str(dtaware_changes_tz(self.object.dt_to, self.request.local_zone))
        return d
        
    def form_valid(self, form):
        if form.instance.type==StrategiesTypes.PairsInSameAccount:
            if form.instance.additional1 is None or form.instance.additional2 is None or form.instance.additional3 is None:
                form.add_error(None, ValidationError({"type": "Additional 1, 2 and 3 can't be empty"}))                
                return super().form_invalid(form)
        return super().form_valid(form)
        

@method_decorator(login_required, name='dispatch')
class strategy_delete(DeleteView):
    model = Strategies
    template_name = 'strategy_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('strategy_list_active')
        

@method_decorator(login_required, name='dispatch')
class investment_new(CreateView):
    model = Investments
    template_name="investment_new.html"
    fields = ( 'name', 'selling_price', 'products',  'selling_expiration',  'daily_adjustment', 'balance_percentage', 'active')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investment_new, self).get_form(form_class)
        form.fields['name'].widget = forms.TextInput()
        return form
    
    def get_context_data(self, **kwargs):
        context = super(investment_new, self).get_context_data(**kwargs)
        context['account'] = Accounts.objects.get(pk=self.kwargs['accounts_id'])
        return context

    def get_initial(self):
        return {
            'daily_adjustment': False, 
            'balance_percentage': 100, 
            'selling_price': 0, 
            'active': True
        }
    def form_valid(self, form):
        form.instance.accounts =Accounts.objects.get(pk=self.kwargs['accounts_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.id,))
        
        
@login_required
def investment_change_active(request, pk):
    investment=get_object_or_404(Investments, id=pk)
    investment.active=not investment.active
    investment.save()
    return HttpResponseRedirect(reverse("investment_view", args=(investment.id, )))
    
@login_required
def investment_ranking(request):
    ldo=LdoInvestmentsRanking(request)
    return render(request, 'investment_ranking.html', locals())

@method_decorator(login_required, name='dispatch')
class investment_update(SuccessMessageMixin, UpdateView):
    queryset = Investments.objects.select_related("products").select_related("products__productstypes").select_related("products__leverages")
    fields = ( 'name', 'selling_price', 'products',  'selling_expiration',  'daily_adjustment', 'balance_percentage', 'active')
    template_name="investment_update.html"

    def get_success_message(self, cleaned_data):
        return Investments.bank_alert(cleaned_data)
        
    def get_initial(self):
        return {
            'selling_expiration': str(self.object.selling_expiration), 
            }

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.id,))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investment_update, self).get_form(form_class)
        form.fields['name'].widget = forms.TextInput()
        widget_date(self.request, form.fields['selling_expiration'])
        self.investments_operations=InvestmentsOperations_from_investment(self.request, self.object, timezone.now(), self.request.local_currency)
        return form

@method_decorator(login_required, name='dispatch')
class investment_delete(DeleteView):
    model = Investments
    template_name = 'investment_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('investment_list_active')
        
@method_decorator(login_required, name='dispatch')
class order_new(SuccessMessageMixin, CreateView):
    model = Orders
    template_name="order_new.html"
    fields = ( 'date', 'expiration', 'investments',  'shares',  'price')

    def get_success_message(self, cleaned_data):
        return Orders.bank_alert(cleaned_data)

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(order_new, self).get_form(form_class)
        widget_date(self.request, form.fields['date'])
        widget_date(self.request, form.fields['expiration'])
        form.fields['investments'].queryset=Investments.queryset_for_investments_products_combos_order_by_fullname()
        return form
    
    def get_initial(self):
        return {
            'date': str(date.today()), 
            'price': self.request.GET.get("price", 0),
            'shares': self.request.GET.get("shares", 0),
        }

    def get_success_url(self):
        return reverse_lazy('order_list_active')
        
@method_decorator(login_required, name='dispatch')
class order_update(SuccessMessageMixin, UpdateView):
    model = Orders
    fields = ( 'date', 'expiration', 'investments',  'shares',  'price')
    template_name="order_update.html"

    def get_success_message(self, cleaned_data):
        return Orders.bank_alert(cleaned_data)

    def get_initial(self):
        return {
            'date': str(self.object.date), 
            'expiration': str(self.object.expiration), 
            }

    def get_success_url(self):
        return reverse_lazy('order_list_active')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(order_update, self).get_form(form_class)
        widget_date(self.request, form.fields['date'])
        widget_date(self.request, form.fields['expiration'])
        form.fields['investments'].queryset=Investments.queryset_for_investments_products_combos_order_by_fullname()
        return form

@method_decorator(login_required, name='dispatch')
class order_delete(DeleteView):
    model = Orders
    template_name = 'order_delete.html'

    def get_success_message(self, cleaned_data):
        return 
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Order was successfully deleted. Please delete it from your bank if necessary."))#SuccessMessageMixin Needs form valid
        return super(DeleteView, self).delete(request, *args, **kwargs)


    def get_success_url(self):
        return reverse_lazy('order_list_active')

@method_decorator(login_required, name='dispatch')
class dividend_new(CreateView):
    model = Dividends
    template_name="dividend_new.html"
    fields = ( 'datetime', 'concepts', 'gross',  'net',  'taxes', 'commission',  'dps',  'currency_conversion')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(dividend_new, self).get_form(form_class)
        widget_datetime(self.request, form.fields["datetime"])
        form.fields['concepts'].queryset=Concepts.queryset_for_dividends_order_by_fullname()
        return form
    
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.local_zone)), 
            'currency_conversion':1, 
            'gross':0, 
            'net':0, 
            'taxes':0, 
            'commission':0, 
            'dps':0, 
            }

    @transaction.atomic
    def form_valid(self, form):
        form.instance.investments= Investments.objects.get(pk=self.kwargs['investments_id'])
        if ( form.instance.commission>=0 and form.instance.taxes>=0) :
            form.instance.save()
            accountoperation=form.instance.update_associated_account_operation()
            form.instance.accountsoperations=accountoperation
            form.instance.save()#To save accountsoperations
            return super().form_valid(form)
        else:
            if form.instance.commission<0:
                form.add_error(None, ValidationError({"commission": "Commission must be positive ..."}))    
            if form.instance.taxes<0:
                form.add_error(None, ValidationError({"taxes": "Taxes must be positive ..."}))    
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))
        
@method_decorator(login_required, name='dispatch')
class dividend_update(UpdateView):
    model = Dividends
    template_name="dividend_update.html"
    fields = ( 'datetime', 'concepts', 'gross',  'net',  'taxes', 'commission',  'dps',  'currency_conversion')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(dividend_update, self).get_form(form_class)
        widget_datetime(self.request, form.fields['datetime'] )
        form.fields['concepts'].queryset=Concepts.queryset_for_dividends_order_by_fullname()
        return form

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))
        
        
    @transaction.atomic
    def form_valid(self, form):
        form.instance.investments= Dividends.objects.get(pk=self.kwargs['pk']).investments
        if ( form.instance.commission>=0 and form.instance.taxes>=0) :
            form.instance.save()
            accountoperation=form.instance.update_associated_account_operation()
            form.instance.accountsoperations=accountoperation
            form.instance.save()#To save accountsoperations
            return super().form_valid(form)
        else:
            if form.instance.commission<0:
                form.add_error(None, ValidationError({"commission": "Commission must be positive ..."}))    
            if form.instance.taxes<0:
                form.add_error(None, ValidationError({"taxes": "Taxes must be positive ..."}))    
            return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class dividend_delete(DeleteView):
    model = Dividends
    template_name = 'dividend_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))
        
    @transaction.atomic
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete_associated_account_operation()
        return super(dividend_delete, self).delete(*args, **kwargs)




## Sets a datetime widget for django forms
## @param initial datetime or "now" or None or "". If None pass. If "" returns it empty field. If "now" returns current. If datetime resturns datetime
def widget_datetime(request, field):
    field.widget.attrs['is'] ='input-datetime'
    field.widget.attrs['localzone'] =request.local_zone
    field.widget.attrs['locale'] =request.LANGUAGE_CODE
#    if initial is not None:
#        if initial == "now":
#            field.initial= str(dtaware_changes_tz(timezone.now(), request.local_zone))
#        elif initial == "":
#            field.initial= ""
#        else:
#            field.initial=str(dtaware_changes_tz(initial, request.local_zone))

## Sets a datetime widget for django forms
## @param initial date or "today" or None or "". If None pass. If "" returns it empty field. If "today" returns current. If date resturns date
def widget_date(request, field):
    field.widget.attrs['is'] ='input-date'
    field.widget.attrs['locale'] =request.LANGUAGE_CODE
#        if initial is not None:
#        if initial =="today":
#            field.initial=str(date.today())
#        elif initial == "":
#            field.initial=""
#        else:
#            field.initial=str(initial)
    
def widget_currency_conversion(request, field, from_currency, to_currency):
    field.widget.attrs['is']='input-currency-factor'
    field.widget.attrs['from'] = from_currency
    field.widget.attrs['to'] = to_currency
        #del form.fields['currency_conversion'].widget.attrs['step']
    #field.widget.attrs['type']="text"
