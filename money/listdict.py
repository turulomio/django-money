## Module that uses dictionaries and list of dictionaries to prepare data for django
## Object types:
## - Dictionary (d)
## - List of dicionaries (ld)
## - List of dictionaries object (ldo)
##
## Methods
## - d_ClassName_KeyName. To add a KeyName to dictionary d of the type Classname. No database querys
## - LdoName. Encapsulates everything, like tables, database querys although  we must try to avoid it
## - ld_ClassName. No database querys
## Predefined dictionaries in models
## - d_product_with_basic. Product with
## - d_investment_with_operations. Investment with operations
## Predefined list of dictionaries
## - ld_investments List of Investments with fields of database
## - ld_investments_with_operations. List of d_investment_with_operations
## Predefined querysets
## 


## List dict is the main 

## LD_ADD. Adds a new key to all dicts in the lists
## LD_TOTAL. Calculates a total using a listdict returning a value
## LD_DEL. Delets a key

import asyncio
from asgiref.sync import sync_to_async
from datetime import date, timedelta
from decimal import Decimal
from money.connection_dj import  cursor_rows
from money.reusing.listdict_functions import listdict2dict, listdict_print,  Ldo
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from xulpymoney.libxulpymoneytypes import eOperationType
from money.models import (
    Accounts, 
    Comment, 
    Concepts, 
    Dividends, 
    Investments, 
    Operationstypes, 
    Productstypes, 
    Strategies, 
    balance_user_by_operationstypes,
    percentage_to_selling_point, 
    total_balance, 
    currencies_in_accounts, 
    qs_investments_netgains_usercurrency_in_year_month, 
    money_convert, 
)
from money.reusing.casts import string2list_of_integers, valueORempty
from money.reusing.currency import Currency
from money.reusing.datetime_functions import dtaware_month_end, months
from money.reusing.decorators import timeit
from money.investmentsoperations import InvestmentsOperationsManager_from_investment_queryset, InvestmentsOperationsTotals_from_investment, IOC, InvestmentsOperations_from_investment, InvestmentsOperationsTotalsManager_from_all_investments
from money.reusing.percentage import percentage_between, Percentage
from money.reusing.tabulator import TabulatorFromListDict
from concurrent.futures import ThreadPoolExecutor, as_completed

ld_print=listdict_print

## Class that return a object to manage listdict
## El objetivo es crear un objeto list_dict que se almacenera en self.ld con funciones set
## set_from_db #Todo se carga desde base de datos con el minimo parametro posible
## set_from_db_and_variables #Preguntara a base datos aquellas variables que falten. Aunque no estén en los parámetros p.e. money_convert
## set_from_variables #Solo con variables
## set #El listdict ya está hecho pero se necesita el objeto para operar con el
class LdoDjangoMoney(Ldo):
    def __init__(self, request, name=None):
        Ldo.__init__(self, name)
        self.request=request

def listdict_accounts(queryset, local_currency):
    list_=[]
    for account in queryset:
        balance=account.balance(timezone.now(), local_currency)
        list_.append({
                "id": account.id, 
                "active":account.active, 
                "name": account.fullName(), 
                "number": account.number,
                "balance": balance[0].string(),  
                "balance_user": balance[1], 
            }
        )
    return list_    

def listdict_investments(queryset, dt,  local_currency, active):
    list_=[]
    
    if active is True:
        for investment in queryset:
            iot=InvestmentsOperationsTotals_from_investment(investment, dt, local_currency)
            basic_quotes=investment.products.basic_results()
            try:
                daily_diff=(basic_quotes['last']-basic_quotes['penultimate'])*iot.io_total_current["shares"]*investment.products.real_leveraged_multiplier()
            except:
                daily_diff=0
            list_.append({
                    "id": investment.id, 
                    "active":investment.active, 
                    "name": investment.fullName(), 
                    "last_datetime": basic_quotes['last_datetime'], 
                    "last_quote": basic_quotes['last'], 
                    "daily_difference": daily_diff, 
                    "daily_percentage":percentage_between(basic_quotes['penultimate'], basic_quotes['last']),             
                    "invested_local": iot.io_total_current["invested_user"], 
                    "balance": iot.io_total_current["balance_user"], 
                    "gains": iot.io_total_current["gains_gross_user"],  
                    "percentage_invested": Percentage(iot.io_total_current["gains_gross_user"], iot.io_total_current["invested_user"]), 
                    "percentage_sellingpoint": percentage_to_selling_point(iot.io_total_current["shares"], investment.selling_price, basic_quotes['last']), 
                    "selling_expiration": investment.selling_expiration, 
                }
            )
    else:        
        for investment in queryset:
            list_.append({
                "id": investment.id, 
                "active":investment.active, 
                "name": investment.fullName(), 
            })
    return list_

def listdict_banks(request, queryset, dt, active):
    list_=[]
    
    iotm=InvestmentsOperationsTotalsManager_from_all_investments(request, dt)
    for bank in queryset:
        accounts_balance=Accounts.accounts_balance_user_currency(bank.accounts(active), timezone.now())
        investments_balance =0
        for investment in bank.investments(active):
            investments_balance=investments_balance+iotm.find_by_id(investment.id).io_total_current["balance_user"]
        list_.append({
                "id": bank.id, 
                "active":bank.active, 
                "name": bank.name, 
                "accounts_balance": accounts_balance, 
                "investments_balance": investments_balance, 
                "total_balance": accounts_balance+investments_balance
            }
        )
    return list_

## @param ohclmonthly If none load then in this function
def listdict_product_quotes_month_comparation(first_year, product, ohclmonthly=None):
    #Calculo 1 mes antes
    rows_month=cursor_rows("""
WITH quotes as (
	SELECT 
		dates::date - interval '1 day' date, 
		(select quote from quote(%s, dates - interval '1 day')), 
		lag((select quote from quote(%s, dates - interval '1 day')),1) over(order by dates::date) 
	from 
		generate_series('%s-01-01'::date - interval '1 day','%s-01-01'::date, '1 month') dates
)
select date,lag, quote, percentage(lag,quote)  from quotes;
""", (product.id, product.id, first_year, date.today().year+1))
    rows_month.pop(0)
    
    #Calculo 1 año antes
    rows_year=cursor_rows("""
WITH quotes as (
	SELECT 
		dates::date - interval '1 day' date, 
		(select quote from quote(%s, dates - interval '1 day')), 
		lag((select quote from quote(%s, dates - interval '1 day')),1) over(order by dates::date) 
	from 
		generate_series('%s-01-01'::date - interval '1 day','%s-01-02'::date, '1 year') dates
)
select date, lag, quote, percentage(lag,quote)  from quotes;
""", (product.id, product.id, first_year, date.today().year+1))
    rows_year.pop(0)
#    ld_print(rows_month)
#    ld_print(rows_year)
    #PERCENTAGES
    ld_percentage=[]
    d={ 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    for i in range(0, len(rows_month)):
        month=(i % 12 )+1
        d[month]=rows_month[i]["percentage"]
        if month==12:
            ld_percentage.append(d)
            d={ 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    if month!=12:
        ld_percentage.append(d)

    for i in range(0, len(rows_year)):
        ld_percentage[i]["year"]=first_year+i 
        ld_percentage[i][13]=rows_year[i]["percentage"]
        
    #QUOTES
    ld_quotes=[]
    d={ 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    for i in range(0, len(rows_month)):
        month=(i % 12 )+1
        d[month]=rows_month[i]["quote"]
        if month==12:
            ld_quotes.append(d)
            d={ 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    if month!=12:
        ld_quotes.append(d)

    for i in range(0, len(rows_year)):
        ld_quotes[i]["year"]=first_year+i 

    return ld_quotes, ld_percentage

## Gets all ioh from all investments 
def listdict_investmentsoperationshistorical(year, month, local_currency, local_zone):
    #Git investments with investmentsoperations in this year, month
    list_ioh=[]
    dict_ot=Operationstypes.dictionary()
    dt_year_month=dtaware_month_end(year, month, local_zone)
    for investment in Investments.objects.raw("select distinct(investments.*) from investmentsoperations, investments where date_part('year', datetime)=%s and date_part('month', datetime)=%s and investments.id=investmentsoperations.investments_id", (year, month)):
        investments_operations=InvestmentsOperations_from_investment(investment, dt_year_month, local_currency)
        
        for ioh in investments_operations.io_historical:
            if ioh['dt_end'].year==year and ioh['dt_end'].month==month:
                ioh["name"]=investment.fullName()
                ioh["operationstypes"]=dict_ot[ioh["operationstypes_id"]]
                ioh["years"]=0
                list_ioh.append(ioh)
    list_ioh= sorted(list_ioh,  key=lambda item: item['dt_end'])
    return list_ioh

## Different o Heterogeneus, due to sum shares...
class LdoInvestmentsOperationsCurrentHeterogeneusSameProductInAccount(LdoDjangoMoney):
    def __init__(self, request, name):
        LdoDjangoMoney.__init__(self, request, name)

    def set_from_db_and_variables(self, d_product_with_basics, account):
        self.d_product_with_basics=d_product_with_basics
        
        list_ioc=[]
        dict_ot=Operationstypes.dictionary()
        for investment in Investments.objects.raw("""
select 
    distinct(investments.*) 
from 
    investmentsoperations, 
    investments 
where 
    investments.products_id=%s and 
    investments.accounts_id=%s and 
    investments.id=investmentsoperations.investments_id""", ( d_product_with_basics["id"], account.id)):
            io=investment.operations(self.request.local_currency)
            
            
            for ioc in io.io_current:
                o=IOC(investment, ioc)
                ioc["name"]=investment.fullName()
                ioc["operationstypes"]=self.request.operationstypes[ioc["operationstypes_id"]]
                ioc["percentage_annual"]=o.percentage_annual()
                ioc["percentage_apr"]=o.percentage_apr()
                ioc["percentage_total"]=o.percentage_total()
                ioc["operationstypes"]=dict_ot[ioc["operationstypes_id"]]
                list_ioc.append(ioc)
        self.ld=list_ioc
        return self

    def shares(self):
        return self.sum("shares")

    def shares_js(self):
        return str(self.shares()).replace(",", ".")
        
    def average_price_user(self):
        return self.average_ponderated("shares", "price_user")
        
    def tabulator(self):
        r=TabulatorFromListDict(f"{self.name}_table")
        r.setDestinyUrl(None)
        r.setLocalZone(self.request.local_zone)
        r.setListDict(self.ld)
        r.setFields("id","datetime", "name","operationstypes",  "shares", "price_investment", "invested_investment", "balance_investment", "gains_gross_investment", "percentage_annual", "percentage_apr", "percentage_total")
        r.setHeaders("Id", _("Date and time"), _("Name"),  _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
        r.setTypes("int","datetime", "str", "str",  "Decimal", self.d_product_with_basics['currency'], self.d_product_with_basics['currency'], self.d_product_with_basics['currency'],  self.d_product_with_basics['currency'], "percentage", "percentage", "percentage")
        r.setBottomCalc(None, None, None, None, "sum", None,  "sum", "sum", "sum", None, None, None)
        r.showLastRecord(False)
        return r.render()
        
    def invested(self):
        return self.sum("invested_user")
        
    def gains_gross_user(self):
        return self.sum("gains_gross_user")
        
    ## Devuelve el saldo de la inversión para cfd, ya que el saldo es 0 para cfd xq son contratos.
    def balance_cfd(self):
        return Currency(self.invested()+self.gains_gross_user(), self.request.local_currency)


#GOOD JOB
class LdoProductsPairsEvolution(LdoDjangoMoney):
    def __init__(self, request, name):
        LdoDjangoMoney.__init__(self, request, name)        
        
    def set_from_db_and_variables(self, product_worse, product_better, ioc_worse, ioc_better, basic_results_worse,   basic_results_better, name=None):
        self.product_worse=product_worse
        self.product_better=product_better
        self.ioc_worse=ioc_worse
        self.ioc_better=ioc_better
        self.basic_results_worse=basic_results_worse
        self.basic_results_better=basic_results_better

        ## Get listdict
        l=[]
        first_pr=0
        for i in range(len(ioc_better)):
            price_better=money_convert(ioc_better[i]["datetime"], ioc_better[i]["price_investment"], product_better.currency, product_worse.currency)
            price_worse=ioc_worse[i]["price_investment"]
            price_ratio=price_better/price_worse
            if i==0:
                first_pr=price_ratio
            invested=abs(ioc_better[i]["invested_user"])+abs(ioc_worse[i]["invested_user"])
            l.append({
                "datetime":ioc_better[i ]["datetime"], 
                "invested": invested, 
                "price_worse": price_worse, 
                "price_better": price_better, 
                "price_ratio": price_ratio, 
                "percentage_pr": percentage_between(first_pr, price_ratio),
            })
        price_better_last=money_convert(timezone.now(), basic_results_better["last"], product_better.currency, product_worse.currency)
        price_worse_last=basic_results_worse["last"]
        price_ratio_last=price_better_last/price_worse_last
        l.append({
            "datetime":timezone.now(), 
            "invested": 0, 
            "price_worse": price_worse_last, 
            "price_better": price_better_last, 
            "price_ratio": price_better_last/price_worse_last, 
            "percentage_pr": percentage_between(first_pr, price_ratio_last),
        })
        l= sorted(l,  key=lambda item: item['datetime'])
        self.ld=l
        return self
        
    def price_ratio_ponderated_average(self):
        sum_inv=0
        sum_inv_pr=0
        for i in range(len(self.ioc_better)):            
            price_better=money_convert(self.ioc_better[i]["datetime"], self.ioc_better[i]["price_investment"], self.product_better.currency, self.product_worse.currency)
            price_ratio=price_better/self.ioc_worse[i]["price_investment"]
            invested=abs(self.ioc_better[i]["invested_user"])+abs(self.ioc_worse[i]["invested_user"])
            sum_inv=sum_inv+invested
            sum_inv_pr=sum_inv_pr+invested*price_ratio
        return sum_inv_pr/sum_inv

    def tabulator(self):
        r=TabulatorFromListDict(f"{self.name}_table")
        r.setDestinyUrl(None)
        r.setLocalZone(self.request.local_zone)
        r.setListDict(self.ld)
        r.setFields("datetime", "invested",  "price_better","price_worse","price_ratio", "percentage_pr")
        r.setHeaders(_("Date and time"), _("Invested"), _("Price better"), _("Price worse"), _("Price ratio"), _("% price ratio from start"))
        r.setTypes("datetime", self.request.local_currency, self.request.local_currency, self.request.local_currency, "Decimal6", "percentage")
        r.showLastRecord(False)
        return r.render()

def listdict_products_pairs_evolution_from_datetime(product_worse, product_better, common_quotes, basic_results_worse,   basic_results_better):
    l=[]
    last_pr=Percentage(0, 1)
    first_pr=common_quotes[0]["b_open"]/common_quotes[0]["a_open"]
    for row in common_quotes:#a worse, b better
        pr=row["b_open"]/row["a_open"]
        l.append({
            "datetime": row["date"], 
            "price_worse": row["a_open"], 
            "price_better": row["b_open"], 
            "price_ratio": pr, 
            "price_ratio_percentage_from_start": percentage_between(first_pr, pr), 
            "price_ratio_percentage_month_diff": percentage_between(last_pr, pr)
        })
        last_pr=pr
    return l

def listdict_products_pairs_evolution_to_filter_reinvest(product_worse, product_better, common_quotes, basic_results_worse,   basic_results_better):
    l=[]
    last_pr=Percentage(0, 1)
    first_pr=common_quotes[0]["b_open"]/common_quotes[0]["a_open"]
    for row in common_quotes:#a worse, b better
        pr=row["b_open"]/row["a_open"]
        l.append({
            "datetime": row["date"], 
            "price_worse": row["a_open"], 
            "price_better": row["b_open"], 
            "price_ratio": pr, 
            "price_ratio_percentage_from_start": percentage_between(first_pr, pr), 
            "price_ratio_percentage_month_diff": percentage_between(last_pr, pr)
        })
        last_pr=pr
    return l


def listdict_report_total_income(qs_investments, year, local_currency, local_zone):
    def month_results(year,  month, month_name):
        dividends=Dividends.netgains_dividends(year, month)
        incomes=balance_user_by_operationstypes(year,  month,  eOperationType.Income, local_currency, local_zone)-dividends
        expenses=balance_user_by_operationstypes(year,  month,  eOperationType.Expense, local_currency, local_zone)
        
        start=timezone.now()
        gains=qs_investments_netgains_usercurrency_in_year_month(qs_investments, year, month, local_currency, local_zone)
        print("Loading list netgains opt took {} (CUELLO BOTELLA UNICO)".format(timezone.now()-start))        
        
        total=incomes+gains+expenses+dividends
        
        return month_name, month,  year,  incomes, expenses, gains, dividends, total
    list_=[]
    futures=[]
    
    
    # HA MEJORADO UNOS 3 segundos de 16 a 13
    with ThreadPoolExecutor(max_workers=settings.CONCURRENCY_DB_CONNECTIONS_BY_USER) as executor:
        for month_name, month in (
            (_("January"), 1), 
            (_("February"), 2), 
            (_("March"), 3), 
            (_("April"), 4), 
            (_("May"), 5), 
            (_("June"), 6), 
            (_("July"), 7), 
            (_("August"), 8), 
            (_("September"), 9), 
            (_("October"), 10), 
            (_("November"), 11), 
            (_("December"), 12), 
        ):
            futures.append(executor.submit(month_results, year, month, month_name))
        
        for future in as_completed(futures):
            #print(future, future.result())
            month_name, month,  year,  incomes, expenses, gains, dividends, total = future.result()
            list_.append({
                "id": f"{year}/{month}/", 
                "month_number":month, 
                "month": month_name,
                "incomes":incomes, 
                "expenses":expenses, 
                "gains":gains, 
                "dividends":dividends, 
                "total":total,  
            })
            
    list_= sorted(list_, key=lambda item: item["month_number"])
    return list_

def listdict_report_total(year, last_year_balance, local_currency, local_zone):
    def month_results(month_end, month_name, local_currency):
        return month_end, month_name, total_balance(month_end, local_currency)
    #####################
    list_=[]
    futures=[]
    
    # HA MEJORADO UNOS 5 segundos de 7 a 2
    with ThreadPoolExecutor(max_workers=settings.CONCURRENCY_DB_CONNECTIONS_BY_USER) as executor:
        for month_name, month in (
            (_("January"), 1), 
            (_("February"), 2), 
            (_("March"), 3), 
            (_("April"), 4), 
            (_("May"), 5), 
            (_("June"), 6), 
            (_("July"), 7), 
            (_("August"), 8), 
            (_("September"), 9), 
            (_("October"), 10), 
            (_("November"), 11), 
            (_("December"), 12), 
        ):
        
            month_end=dtaware_month_end(year, month, local_zone)
            futures.append(executor.submit(month_results, month_end,  month_name, local_currency))

    futures= sorted(futures, key=lambda future: future.result()[0])#month_end
    last_month=last_year_balance.amount
    for future in futures:
        month_end, month_name,  total = future.result()
        list_.append({
            "month_number":month_end, 
            "month": month_name,
            "account_balance":total['accounts_user'], 
            "investment_balance":total['investments_user'], 
            "total":total['total_user'] , 
            "percentage_year": percentage_between(last_year_balance.amount, total['total_user'] ), 
            "diff_lastmonth": total['total_user']-last_month, 
        })
        last_month=total['total_user']
    for d in list_:
        print(d["total"],  last_year_balance)
    return list_
    
def listdict_dividends_from_queryset(qs_dividends):
    r=[]
    for o in qs_dividends:
        r.append({"id":o.id, "datetime":o.datetime, "concepts":o.concepts.name, "gross":o.gross, "net":o.net, "taxes":o.taxes, "commission":o.commission})
    return r

def listdict_dividends_by_month(year, month):
    qs_dividends=Dividends.objects.all().filter(datetime__year=year, datetime__month=month).order_by('datetime')
    return listdict_dividends_from_queryset(qs_dividends)

    
def listdict_accountsoperations_from_queryset(qs_accountsoperations, initial):
    r=[]
    balance=Decimal(initial)
    for op in qs_accountsoperations:
        balance=balance+op.amount
        r.append({"id":op.id, "datetime": op.datetime,"concepts": op.concepts.name,"amount":op.amount,"balance": balance,"comment": Comment().decode(op.comment)})
    r= sorted(r,  key=lambda item: item['datetime'])
    return r


def listdict_accountsoperations_creditcardsoperations_by_operationstypes_and_month(year, month, operationstypes_id, local_currency, local_zone):
    
    r=[]
    dict_concepts=Concepts.dictionary()
    balance=0
    for currency in currencies_in_accounts():
        for op in cursor_rows("""
            select datetime,concepts_id, amount, comment
            from 
                accountsoperations,
                accounts
            where 
                operationstypes_id=%s and 
                date_part('year',datetime)=%s and
                date_part('month',datetime)=%s and
                accounts.currency=%s and
                accounts.id=accountsoperations.accounts_id   
        union all 
            select datetime,concepts_id, amount, comment
            from 
                creditcardsoperations ,
                creditcards,
                accounts
            where 
                operationstypes_id=%s and 
                date_part('year',datetime)=%s and
                date_part('month',datetime)=%s and
                accounts.currency=%s and
                accounts.id=creditcards.accounts_id and
                creditcards.id=creditcardsoperations.creditcards_id""", (operationstypes_id, year, month,  currency, operationstypes_id, year, month,  currency)):
            if local_currency==currency:
                balance=balance+op["amount"]
                r.append({"id":-1, "datetime": op['datetime'], "concepts":dict_concepts[op['concepts_id']], "amount":op['amount'], "balance": balance,"comment":Comment().decode(op["comment"])})
            else:
                print("TODO")
            
        r= sorted(r,  key=lambda item: item['datetime'])
#            r=r+money_convert(dtaware_month_end(year, month, local_zone), balance, currency, local_currency)
    return r
    
    
    
def listdict_strategies(request, active):
    l=[]
    qs_strategies=Strategies.objects.all().filter(dt_to__isnull=active)
    for strategy in qs_strategies:
        investments_ids=string2list_of_integers(strategy.investments)
        qs_investments_in_strategy=Investments.objects.filter(id__in=(investments_ids))
        io_in_strategy=InvestmentsOperationsManager_from_investment_queryset(qs_investments_in_strategy, timezone.now(), request)
        
        gains_net_current=io_in_strategy.current_gains_net_user()        
        dt_to=timezone.now() if strategy.dt_to is None else strategy.dt_to
        gains_net_historical=io_in_strategy.historical_gains_net_user_between_dt(strategy.dt_from, dt_to)
        dividends_net=Dividends.net_gains_baduser_between_datetimes_for_some_investments(investments_ids, strategy.dt_from, dt_to)
        
        l.append({
                "id": strategy.id, 
                "name": strategy.name, 
                "dt_from":strategy.dt_from, 
                "dt_to":strategy.dt_to, 
                "gains_net_current": gains_net_current, 
                "gains_net_historical": gains_net_historical, 
                "dividends_net": dividends_net, 
                "total_net": gains_net_current+gains_net_historical+dividends_net
            }
        )
    return l


    
def listdict_orders( qs_orders):
    l=[]
    for o in qs_orders:
        basic_results=o.investments.products.basic_results()
        l.append({
            "id": o.id, 
            "name": f"{o.investments.name} ({o.investments.accounts.name})", 
            "date": o.date, 
            "expiration": valueORempty(o.expiration), 
            "shares": o.shares, 
            "price": o.price, 
            "amount": o.shares*o.price*o.investments.products.real_leveraged_multiplier(), 
            "percentage_from_price": percentage_between( basic_results["last"], o.price), 
            "currency": o.investments.products.currency, 
            "executed": o.executed, 
        })
    return l
        
    
def listdict_investments_gains_by_product_type(year, local_currency):
    gains=cursor_rows("""
select 
    investments.id, 
    productstypes_id, 
    (investment_operations(investments.id, make_timestamp(%s,12,31,23,59,59)::timestamp with time zone, %s)).io_historical 
from  
    investments, 
    products 
where investments.products_id=products.id""", (year, local_currency, ))
    
    #This inner joins its made to see all productstypes_id even if they are Null.
    # Subquery for dividends is used due to if I make a where from dividends table I didn't get null productstypes_id
    dividends=cursor_rows("""
select  
    productstypes_id, 
    sum(dividends.gross) as gross,
    sum(dividends.net) as net
from 
    products
    left join investments on products.id=investments.products_id
    left join (select * from dividends where extract('year' from datetime)=%s) dividends on investments.id=dividends.investments_id
group by productstypes_id""", (year, ))
    dividends_dict=listdict2dict(dividends, "productstypes_id")
    l=[]
    for pt in Productstypes.objects.all():
        gains_net, gains_gross= 0, 0
        for row in gains:
            if row["productstypes_id"]==pt.id:
                io_historical=eval(row["io_historical"])
                for ioh in io_historical:
                    if int(ioh["dt_end"][0:4])==year:
                        gains_net=gains_net+ioh["gains_net_user"]
                        gains_gross=gains_gross+ioh["gains_gross_user"]

        l.append({
                "id": pt.id, 
                "name":pt.name, 
                "gains_gross": gains_gross, 
                "dividends_gross":dividends_dict[pt.id]["gross"], 
                "gains_net":gains_net, 
                "dividends_net": dividends_dict[pt.id]["net"], 
        })
    return l

@timeit
def listdict_chart_total_threadpool(year_from, local_currency, local_zone):
    def month_results(year, month,  local_currency, local_zone):
        dt=dtaware_month_end(year, month, local_zone)
        return dt, total_balance(dt, local_currency)
    #####################
    if year_from==date.today().year:
        months_12=date.today()-timedelta(days=365)
        list_months=months(months_12.year, months_12.month)
    else:
        list_months=months(year_from, 1)
        
    l=[]
    futures=[]
    
    # HA MEJORADO UNOS 5 segundos de 10 segundos a 3 para 12 meses
    with ThreadPoolExecutor(max_workers=settings.CONCURRENCY_DB_CONNECTIONS_BY_USER) as executor:
        for year,  month in list_months:    
            futures.append(executor.submit(month_results, year, month, local_currency,  local_zone))

#    futures= sorted(futures, key=lambda future: future.result()[0])#month_end
    for future in futures:
        dt, total=future.result()
        l.append({
            "datetime":dt, 
            "total_user": total["total_user"], 
            "invested_user":total["investments_invested_user"], 
            "investments_user":total["investments_user"], 
            "accounts_user":total["accounts_user"], 
        })
    return l
    
    
@sync_to_async
def month_results(year, month,  local_currency, local_zone):
    dt=dtaware_month_end(year, month, local_zone)
    return dt, total_balance(dt, local_currency)

@timeit
async def listdict_chart_total_async(year_from, local_currency, local_zone):
    if year_from==date.today().year:
        months_12=date.today()-timedelta(days=365)
        list_months=months(months_12.year, months_12.month)
    else:
        list_months=months(year_from, 1)
        
    l=[]
    futures=[]   
    for year,  month in list_months:
        futures.append(asyncio.ensure_future(month_results(year, month, local_currency,  local_zone)))       
    await asyncio.wait(futures)


    for future in futures:
        dt, total=future.result()
        l.append({
            "datetime":dt, 
            "total_user": total["total_user"], 
            "invested_user":total["investments_invested_user"], 
            "investments_user":total["investments_user"], 
            "accounts_user":total["accounts_user"], 
        })
    return l

def listdict_chart_product_quotes_historical(dt_from, product,  local_currency, local_zone):
    rows=product.ohclDailyBeforeSplits()
    ld_print(rows)
    return rows[-50:]
