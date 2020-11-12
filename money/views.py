import asyncio
from datetime import  date, datetime
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import render,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from math import floor

from money.connection_dj import cursor_rows, cursor_one_column, execute
from money.forms import AccountsOperationsForm, AccountsTransferForm, ProductsRangeForm
from money.charts import (
    chart_lines_total, 
    chart_product_quotes_historical, 
)
from money.tables import (
    TabulatorDividends, 
    TabulatorReportConcepts, 
    TabulatorCreditCardsOperations, 
    TabulatorAccountOperations, 
    TabulatorAccounts, 
    TabulatorBanks, 
    TabulatorConcepts, 
    TabulatorCreditCards, 
    TabulatorInvestments, 
    TabulatorInvestmentsOperationsHomogeneus, 
    TabulatorInvestmentsOperationsCurrentHomogeneus,
    TabulatorProducts, 
    TabulatorOrders, 
    TabulatorReportIncomeTotal, 
    TabulatorReportTotal, 
    TabulatorInvestmentsGainsByProductType, 
    TabulatorInvestmentsOperationsHistoricalHomogeneus, 
    TabulatorInvestmentsOperationsHistoricalHeterogeneus, 
    TabulatorProductsPairsEvolutionWithMonthDiff, 
    TabulatorProductQuotesMonthPercentages, 
    TabulatorProductQuotesMonthQuotes,  
    TabulatorInvestmentsPairsInvestCalculator, 
    TabulatorStrategies
)
from money.reusing.currency import Currency
from money.reusing.datetime_functions import dtaware_month_start, dtaware_month_end, dtaware_changes_tz
from money.reusing.decorators import timeit
from money.reusing.listdict_functions import listdict_sum, listdict_sum_negatives, listdict_sum_positives, listdict_has_key
from money.reusing.percentage import Percentage
from django.utils.translation import ugettext_lazy as _
from money.listdict import (
    LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount, 
    listdict_accounts, 
    listdict_banks, 
    listdict_chart_total_async, 
    listdict_chart_total_threadpool, 
    listdict_chart_product_quotes_historical, 
    listdict_investments, 
    listdict_report_total_income, 
    listdict_report_total,     
    listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month, 
    listdict_accountsoperations_from_queryset, 
    listdict_dividends_by_month, 
    listdict_dividends_from_queryset, 
    listdict_investments_gains_by_product_type, 
    listdict_investmentsoperationshistorical, 
    listdict_orders_active, 
    listdict_product_quotes_month_comparation, 
    LdoProductsPairsEvolution, 
    listdict_products_pairs_evolution_from_datetime, 
    listdict_strategies, 
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
    total_balance, 
)
from xulpymoney.libxulpymoneytypes import eConcept, eComment, eProductType

@login_required
def order_list(request,  active):
    listdict_orders=listdict_orders_active()
    table_orders=TabulatorOrders("table_orders", 'order_update', listdict_orders, request.globals["mem__localcurrency"]).render()
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
        return TabulatorProducts("table_products", 'product_view', listproducts, request.globals["mem__localcurrency"], request.globals["mem__localzone"] )

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
#            if form.cleaned_data['commission']>0:
#                ao_commission=Accountsoperations()
#                ao_commission.datetime=form.cleaned_data['datetime']
#                concept_commision=Concepts.objects.get(pk=eConcept.BankCommissions)
#                ao_commission.concepts=concept_commision
#                ao_commission.operationstypes=concept_commision.operationstypes
#                ao_commission.amount=-form.cleaned_data['commission']
#                ao_commission.accounts=origin
#                ao_commission.save()
#            else:
#                ao_commission=None

           return HttpResponseRedirect( reverse_lazy('product_ranges'))
    else:
        form = ProductsRangeForm()
#        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
#        form.fields['datetime'].widget.attrs['localzone'] =request.globals["mem__localzone"]
#        form.fields['datetime'].widget.attrs['locale'] =request.LANGUAGE_CODE
#        form.fields['datetime'].initial= str(dtaware_changes_tz(timezone.now(), request.globals["mem__localzone"]))
        form.fields['percentage_between_ranges'].initial=5
        form.fields['percentage_gains'].initial=15
        form.fields['amount_to_invest'].initial=5000
  
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
    concepts= Concepts.objects.all().order_by('name')
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
    qsInvestments=Investments.objects.all().select_related('accounts') .filter(pk=7)[0]
    print (qsInvestments.name)
    print(qsInvestments.fullName())
    print(qsInvestments.accounts.name)
    print(qsInvestments.accounts.fullName())
    
    return render(request, 'home.html', locals())

@login_required
def bank_list(request,  active):
    
    banks= Banks.objects.all().filter(active=active).order_by('name')
    banks_list=listdict_banks(banks, timezone.now(), active, request.globals["mem__localcurrency"])
    table_banks=TabulatorBanks("table_banks", 'bank_view', banks_list, request.globals["mem__localcurrency"]).render()
    return render(request, 'bank_list.html', locals())

@login_required
def account_list(request,  active=True):
    
    
    accounts= Accounts.objects.all().filter(active=active).order_by('name')
    list_accounts=listdict_accounts(accounts)
    
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, request.globals["mem__localcurrency"]).render()
    table_accounts=table_accounts.replace(', field:"balance"', ', field:"balance", align:"right"')
    return render(request, 'account_list.html', locals())
        
        
        
@login_required        
def account_view(request, pk, year=date.today().year, month=date.today().month): 
    year_start=1970
    year_end=date.today().year + 10
    
    account=get_object_or_404(Accounts, pk=pk)
    
    dt_initial=dtaware_month_start(year, month, request.globals["mem__localzone"])
    initial_balance=float(account.balance( dt_initial)[0].amount)
    qsaccountoperations= Accountsoperations.objects.all().filter(accounts_id=pk, datetime__year=year, datetime__month=month).order_by('datetime')
    listdic_accountsoperations=listdict_accountsoperations_from_queryset(qsaccountoperations, initial_balance)
    table_accountoperations=TabulatorAccountOperations("table_accountoperations", "accountoperation_update", listdic_accountsoperations, account.currency, request.globals["mem__localzone"]).render()
  
    creditcards= Creditcards.objects.all().filter(accounts_id=pk, active=True).order_by('name')
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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =request.LANGUAGE_CODE
        form.fields['datetime'].initial= str(dtaware_changes_tz(timezone.now(), request.globals["mem__localzone"]))
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
    form_class=AccountsOperationsForm

    def get_form(self, form_class=None): 
        form = super(accountoperation_new, self).get_form(form_class)
        form.fields['accounts'].widget = forms.HiddenInput()
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        form.fields['concepts'].queryset=Concepts.queryset_order_by_fullname()
        return form
        
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.globals["mem__localzone"])), 
            'accounts':Accounts.objects.get(pk=self.kwargs['accounts_id'])
        }
    
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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        return form
        
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(self.object.datetime, self.request.globals["mem__localzone"])), 
        }
    
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)

class accountoperation_delete(DeleteView):
    model = Accountsoperations
    template_name = 'accountoperation_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('account_view',args=(self.object.accounts.id,))

@login_required
def investment_list(request,  active):
    investments= Investments.objects.all().filter(active=active).order_by('name')
    listdict=listdict_investments(investments, timezone.now(), request.globals["mem__localcurrency"], active)
    table_investments=TabulatorInvestments("table_investments", "investment_view", listdict, request.globals["mem__localcurrency"], active, request.globals["mem__localzone"]).render()
    
    # Foot only for active investments
    if listdict_has_key(listdict, "gains"):
        positives=Currency(listdict_sum_positives(listdict, "gains"), request.globals["mem__localcurrency"])
        negatives=Currency(listdict_sum_negatives(listdict, "gains"), request.globals["mem__localcurrency"])
        foot=_(f"Positive gains - Negative gains = {positives} {negatives} = {positives+negatives}")    
    return render(request, 'investment_list.html', locals())
    
@timeit
@login_required
def investment_pairs(request, worse, better, accounts_id):
    localzone=request.globals["mem__localzone"]
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
    
    from money.widgets import table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency
    table_ioc_better_usercurrency=table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency(ldo_ioc_better.ld,  localzone, "table_ioc_better_usercurrency")
    table_ioc_worse_usercurrency=table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency(ldo_ioc_worse.ld,  localzone, "table_ioc_worse_usercurrency")

    pair_gains=Currency(ldo_ioc_better.sum('gains_net_user')+ldo_ioc_worse.sum('gains_net_user'), request.globals["mem__localcurrency"])
    
    datetimes=(ldo_ioc_better.list("datetime")+ldo_ioc_worse.list("datetime")).sort()#List of datetimes

    ldo_products_evolution=LdoProductsPairsEvolution(request,"LdoProductsPairsEvolution")
    ldo_products_evolution.set_from_db_and_variables(product_worse, product_better, datetimes, ldo_ioc_worse.ld, ldo_ioc_better.ld, basic_results_worse,  basic_results_better)
    #Variables to calculate reinvest loses
    gains=ldo_ioc_better.sum("gains_gross_user")+ldo_ioc_worse.sum("gains_gross_user")
    return render(request, 'investment_pairs.html', locals())


@login_required
def ajax_investment_pairs_invest(request, worse, better, accounts_id, amount ):
    product_better=Products.objects.all().filter(id=better)[0]
    product_worse=Products.objects.all().filter(id=worse)[0]
    d_product_better=Products.get_d_product_with_basics(better)
    d_product_worse=Products.get_d_product_with_basics(worse)
    account=Accounts.objects.all().filter(id=accounts_id)[0]    
    list_ioc_better=LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount(d_product_better, account,  request,  name="ldo2_better")
    list_ioc_worse=LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount(d_product_worse, account, request,  name="ldo2_worse")

    listdict=[]
    better_current=list_ioc_better.shares()*product_better.real_leveraged_multiplier()*d_product_better['last']
    better_new_shares=round(amount/d_product_better["last"]/product_better.real_leveraged_multiplier(), 2)
    better_invested=listdict_sum(list_ioc_better.ld, "invested_user")
    better_new= better_new_shares*d_product_better["last"]*product_better.real_leveraged_multiplier()
    better_total=better_current+better_new
    listdict.append({   
        'name': product_better.name, 
        'last_datetime': d_product_better["last_datetime"], 
        'last': d_product_better["last"], 
        'invested': better_invested, 
        'current': better_current, 
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
    table_calculator=TabulatorInvestmentsPairsInvestCalculator("table_calculator", None, listdict, request.globals["mem__localcurrency"], request.globals["mem__localzone"]).render()
    s=f"<p>Difference between pair current balance is {better_current-worse_current}</p>"
    return HttpResponse(table_calculator+ s)
    
@timeit
@ensure_csrf_cookie ##For ajax-button
@login_required
def ajax_investment_pairs_evolution(request, worse, better ):
    product_better=Products.objects.all().filter(id=better)[0]
    product_worse=Products.objects.all().filter(id=worse)[0]
    basic_results_better=product_better.basic_results()
    basic_results_worse=product_worse.basic_results()
    
    if product_better.currency==product_worse.currency:
        common_monthly_quotes=cursor_rows("""
            select 
                make_date(a.year, a.month,1) as date, 
                a.products_id as a, 
                a.open as a_open, 
                b.products_id as b, 
                b.open as b_open 
            from 
                ohclmonthlybeforesplits(%s) as a ,
                ohclmonthlybeforesplits(%s) as b 
            where 
                a.year=b.year and 
                a.month=b.month
        UNION ALL
            select
                now()::date as date,
                %s as a, 
                (select last from last_penultimate_lastyear(%s,now())) as a_open, 
                %s as b, 
                (select last from last_penultimate_lastyear(%s,now())) as b_open
                """, (product_worse.id, product_better.id, 
                product_worse.id, product_worse.id, product_better.id, product_better.id))
    else: #Uses worse currency
        #Fist condition in where it's to remove quotes without money_convert due to no data
        common_monthly_quotes=cursor_rows("""
            select 
                make_date(a.year,a.month,1) as date, 
                a.products_id as a, 
                a.open as a_open, 
                b.products_id as b, 
                money_convert(make_date(a.year,a.month,1)::timestamp with time zone, b.open, %s, %s) as b_open
            from 
                ohclmonthlybeforesplits(%s) as a 
                ,ohclmonthlybeforesplits(%s) as b 
            where 
                b.open != money_convert(make_date(a.year,a.month,1)::timestamp with time zone, b.open, %s, %s)  and
                a.year=b.year and 
                a.month=b.month
        UNION ALL
            select
                now()::date as date,
                %s as a, 
                (select last from last_penultimate_lastyear(%s,now())) as a_open, 
                %s as b, 
                money_convert(now(), (select last from last_penultimate_lastyear(%s,now())), %s,%s) as b_open
                """, ( product_better.currency,  product_worse.currency, 
                        product_worse.id, 
                        product_better.id, 
                        product_better.currency,  product_worse.currency, 
                        
                        product_worse.id,
                        product_worse.id,
                        product_better.id, 
                        product_better.id, product_better.currency,  product_worse.currency))
    
    list_products_evolution=listdict_products_pairs_evolution_from_datetime(product_worse, product_better, common_monthly_quotes, basic_results_worse,  basic_results_better)
    table_products_pair_evolution_from=TabulatorProductsPairsEvolutionWithMonthDiff("table_products_pair_evolution_from", None, list_products_evolution, product_worse.currency, request.globals["mem__localzone"]).render()
    
#    from money.reusing.lineal_regression import LinealRegression
#    lr=LinealRegression(product_better.name, product_worse.name)
#    for row in common_monthly_quotes:
#        lr.append(row["b_open"], row["a_open"])
#        lr.calculate()
#    print(lr.string(True))
#    print(lr.r_squared_string())
    
    return HttpResponse(table_products_pair_evolution_from)

@login_required
def investment_view(request, pk):
    investment=get_object_or_404(Investments, id=pk)
    basic_results=investment.products.basic_results()
    dict_ot=Operationstypes.dictionary()
    io, io_current, io_historical=investment.get_investmentsoperations(timezone.now(), request.globals["mem__localcurrency"])
    
    for ioc in io_current:
        ioc["percentage_annual"]=Investmentsoperations.investmentsoperationscurrent_percentage_annual(ioc, basic_results)
        ioc["percentage_apr"]=Investmentsoperations.investmentsoperationscurrent_percentage_apr(ioc)
        ioc["percentage_total"]=Investmentsoperations.investmentsoperationscurrent_percentage_total(ioc)
        ioc["operationstypes"]=dict_ot[ioc["operationstypes_id"]]
        
    for o in io:
        o["operationstypes"]=dict_ot[o["operationstypes_id"]]

    for ioh in io_historical:
        ioh["operationstypes"]=dict_ot[ioh["operationstypes_id"]]
        ioh["years"]=0
        
    gains_at_selling_price=investment.currency_gains_at_selling_price(io_current)

    table_io=TabulatorInvestmentsOperationsHomogeneus("IO", "investmentoperation_update", io, investment, request.globals["mem__localzone"]).render()
    table_ioc=TabulatorInvestmentsOperationsCurrentHomogeneus("IOC", None, io_current, investment, request.globals["mem__localzone"]).render()
    table_ioh=TabulatorInvestmentsOperationsHistoricalHomogeneus("IOH", None, io_historical, investment, request.globals["mem__localzone"]).render()

    qs_dividends=Dividends.objects.all().filter(investments_id=pk).order_by('datetime')
    listdict_dividends=listdict_dividends_from_queryset(qs_dividends)
    table_dividends=TabulatorDividends("table_dividends", "dividend_update", listdict_dividends, investment.accounts.currency,  request.globals["mem__localzone"]).render()
   
    return render(request, 'investment_view.html', locals())

@method_decorator(login_required, name='dispatch')
class investmentoperation_new(CreateView):
    model = Investmentsoperations
    fields = ( 'datetime', 'operationstypes',  'shares', 'price',  'taxes',  'commission', 'comment', 'currency_conversion')
    template_name="investmentoperation_new.html"

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investmentoperation_new, self).get_form(form_class)
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        form.fields['operationstypes'].queryset=Operationstypes.objects.filter(pk__in=[4, 5, 6])
        return form
                
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.globals["mem__localzone"])), 
            'currency_conversion':1, 
            'taxes':0, 
            'commission':0, 
            }

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))

    @transaction.atomic
    def form_valid(self, form):
        form.instance.investments= Investments.objects.get(pk=self.kwargs['investments_id'])
        if (    form.instance.commission>=0 and 
                form.instance.taxes>=0 and 
                ((form.instance.shares>=0 and form.instance.operationstypes.id in (4, 6)) or (form.instance.shares<0 and form.instance.operationstypes.id==5) )) :
            form.instance.save()
            form.instance.update_associated_account_operation(self.request.globals["mem__localcurrency"])
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
    fields = ( 'datetime', 'operationstypes',  'shares', 'price',  'taxes',  'commission', 'comment', 'currency_conversion')
    template_name="investmentoperation_update.html"
        

    def get_success_url(self):
        return reverse_lazy('investment_view',args=(self.object.investments.id,))

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(investmentoperation_update, self).get_form(form_class) 
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        form.fields['operationstypes'].queryset=Operationstypes.objects.filter(pk__in=[4, 5, 6])
        return form

    @transaction.atomic
    def form_valid(self, form):
        form.instance.investments= Investmentsoperations.objects.get(pk=self.kwargs['pk']).investments
        if (    form.instance.commission>=0 and 
                form.instance.taxes>=0 and 
                ((form.instance.shares>=0 and form.instance.operationstypes.id in (4, 6)) or (form.instance.shares<0 and form.instance.operationstypes.id==5) )) :
            form.instance.save()
            form.instance.update_associated_account_operation(self.request.globals["mem__localcurrency"])
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
    listdic=listdict_investments(investments, timezone.now(), request.globals["mem__localcurrency"], True)
    table_investments=TabulatorInvestments("table_investments", "investment_view", listdic, request.globals["mem__localcurrency"], True, request.globals["mem__localzone"]).render()
    
    accounts= bank.accounts(True)
    list_accounts=listdict_accounts(accounts)
    table_accounts=TabulatorAccounts("table_accounts", "account_view", list_accounts, request.globals["mem__localcurrency"]).render()
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
    last_year=dtaware_month_end(year-1, 12, request.globals["mem__localzone"])
    
    start=timezone.now()
    last_year_balance=Currency(total_balance(last_year, request.globals["mem__localcurrency"])['total_user'], request.globals["mem__localcurrency"])
    print("Loading alltotals last_year took {}".format(timezone.now()-start))
    
    start=timezone.now()
    list_report=listdict_report_total(year, last_year_balance, request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    table_report_total=TabulatorReportTotal("table_report_total", None, list_report, request.globals["mem__localcurrency"]).render()
    print("Loading list report took {}".format(timezone.now()-start))
    
    return render(request, 'report_total.html', locals())



@timeit
@login_required
def ajax_chart_total(request, year_from):
    year_start=1970
    year_end=date.today().year + 10
    ld_chart_total=listdict_chart_total_threadpool(year_from, request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    chart_total=chart_lines_total(ld_chart_total, request.globals["mem__localcurrency"])
    return render(request, 'chart_total.html', locals())

@login_required
def ajax_chart_total_async(request, year_from):
    year_start=1970
    year_end=date.today().year + 10
    start=datetime.now()
    ld_chart_total=asyncio.run(listdict_chart_total_async(year_from, request.globals["mem__localcurrency"], request.globals["mem__localzone"]))
    print(f"listdict_chart_total_async took {datetime.now()-start}")
    chart_total=chart_lines_total(ld_chart_total, request.globals["mem__localcurrency"])
    return render(request, 'chart_total.html', locals())

@timeit
@login_required
def ajax_chart_product_quotes_historical(request, pk):
    product=get_object_or_404(Products, id=pk)
    ld_chart_total=listdict_chart_product_quotes_historical(None, product, request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    chart_total=chart_product_quotes_historical(ld_chart_total, request.globals["mem__localcurrency"])
    return HttpResponse(chart_total)

@timeit
@login_required
def ajax_report_total_income(request, year=date.today().year):  
    qs_investments=Investments.objects.all()
    list_report2=listdict_report_total_income(qs_investments, year, request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    table_report_total_income=TabulatorReportIncomeTotal("table_report_total_income", "report_total_income_details", list_report2, request.globals["mem__localcurrency"]).render()
    return HttpResponse(table_report_total_income)

@timeit
@login_required
def ajax_report_gains_by_product_type(request, year=date.today().year):
    list_report=listdict_investments_gains_by_product_type(year, request.globals["mem__localcurrency"])
    table_investments_gains_by_product_type=TabulatorInvestmentsGainsByProductType("table_investments_gains_by_product_type", None, list_report, request.globals["mem__localcurrency"]).render()
    gross=Currency(listdict_sum(list_report, "dividends_gross")+ listdict_sum(list_report, "gains_gross"), request.globals["mem__localcurrency"])
    net=Currency(listdict_sum(list_report, "dividends_net")+ listdict_sum(list_report, "gains_net"), request.globals["mem__localcurrency"])
    s=f"<p>Gross gains + Gross dividends = {gross.string()}.</p><p>Net gains + Net dividends = {net.string()}.</p>"
    return HttpResponse(table_investments_gains_by_product_type+s)

@timeit
@login_required
def report_total_income_details(request, year=date.today().year, month=date.today()):
    expenses=listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month(year, month, 2,  request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    table_expenses=TabulatorAccountOperations("table_expenses", None, expenses, request.globals["mem__localcurrency"],  request.globals["mem__localzone"]).render()
    incomes=listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month(year, month, 1,  request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    table_incomes=TabulatorAccountOperations("table_incomes", None, incomes, request.globals["mem__localcurrency"],  request.globals["mem__localzone"]).render()
    
    dividends=listdict_dividends_by_month(year, month)
    table_dividends=TabulatorDividends("table_dividends", None, dividends, request.globals["mem__localcurrency"],  request.globals["mem__localzone"]).render()
    
    gains=listdict_investmentsoperationshistorical(year, month, request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    table_gains=TabulatorInvestmentsOperationsHistoricalHeterogeneus("table_gains", None, gains, request.globals["mem__localcurrency"], request.globals["mem__localzone"]).render()
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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        return form
        
    def get_context_data(self, **kwargs):
        context = super(quote_new, self).get_context_data(**kwargs)
        context['product'] = self.product
        return context
        
        
    def get_initial(self):
        self.product=Products.objects.get(pk=self.kwargs['products_id'])
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.globals["mem__localzone"])), 
            'products': self.product
        }
        
    def get_success_url(self):
        return reverse_lazy('investment_list_active')
          
    def form_valid(self, form):
        return super().form_valid(form)

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
    

    table_report_concepts_positive=TabulatorReportConcepts("table_report_concepts_positive", None, list_report_concepts_positive, request.globals["mem__localcurrency"]).render()
    table_report_concepts_negative=TabulatorReportConcepts("table_report_concepts_negative", None, list_report_concepts_negative, request.globals["mem__localcurrency"]).render()

    return render(request, 'report_concepts.html', locals())
    
@login_required
def creditcard_view(request, pk):
    
    
    creditcard=get_object_or_404(Creditcards, id=pk)
    creditcardoperations=Creditcardsoperations.objects.all().filter(creditcards_id=pk,  paid=False)
    table_creditcardoperations=TabulatorCreditCardsOperations("table_creditcardoperations", 'creditcardoperation_update', creditcardoperations, creditcard, request.globals["mem__localzone"]).render()

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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        return form
  
    def form_valid(self, form):
        form.instance.operationstypes = form.cleaned_data["concepts"].operationstypes
        return super().form_valid(form)
    
@login_required
def strategy_list(request, active=True):
    strategies=listdict_strategies(active, request.globals["mem__localcurrency"], request.globals["mem__localzone"])
    table_strategies=TabulatorStrategies("table_strategies", None, strategies, request.globals["mem__localcurrency"]).render()
    return render(request, 'strategy_list.html', locals())
        
        
        
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
        
@method_decorator(login_required, name='dispatch')
class investment_update(UpdateView):
    model = Investments
    fields = ( 'name', 'selling_price', 'products',  'selling_expiration',  'daily_adjustment', 'balance_percentage', 'active')
    template_name="investment_update.html"

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
        form.fields['selling_expiration'].widget.attrs['is'] ='input-date'
        form.fields['selling_expiration'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        return form
    
    def form_valid(self, form):
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class investment_delete(DeleteView):
    model = Investments
    template_name = 'investment_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('investment_list_active')
        
        
@method_decorator(login_required, name='dispatch')
class order_new(CreateView):
    model = Orders
    template_name="order_new.html"
    fields = ( 'date', 'expiration', 'investments',  'shares',  'price')

    def get_form(self, form_class=None): 
        if form_class is None: 
            form_class = self.get_form_class()
        form = super(order_new, self).get_form(form_class)
        form.fields['date'].widget.attrs['is'] ='input-date'
        form.fields['date'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        form.fields['expiration'].widget.attrs['is'] ='input-date'
        form.fields['expiration'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        return form
    
    def get_initial(self):
        return {
            'date': str(date.today()), 
        }
#    def form_valid(self, form):
#        form.instance.accounts =Accounts.objects.get(pk=self.kwargs['accounts_id'])
#        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('order_list_active')
        
@method_decorator(login_required, name='dispatch')
class order_update(UpdateView):
    model = Orders
    fields = ( 'date', 'expiration', 'investments',  'shares',  'price')
    template_name="order_update.html"

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
        form.fields['date'].widget.attrs['is'] ='input-date'
        form.fields['date'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        form.fields['expiration'].widget.attrs['is'] ='input-date'
        form.fields['expiration'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        return form
    
#    def form_valid(self, form):
#        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class order_delete(DeleteView):
    model = Orders
    template_name = 'order_delete.html'
    
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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
        form.fields['concepts'].queryset=Concepts.queryset_for_dividends_order_by_fullname()
        return form
    
    def get_initial(self):
        return {
            'datetime': str(dtaware_changes_tz(timezone.now(), self.request.globals["mem__localzone"])), 
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
        form.fields['datetime'].widget.attrs['is'] ='input-datetime'
        form.fields['datetime'].widget.attrs['localzone'] =self.request.globals["mem__localzone"]
        form.fields['datetime'].widget.attrs['locale'] =self.request.LANGUAGE_CODE
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

