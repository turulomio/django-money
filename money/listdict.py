from datetime import date
from decimal import Decimal
from money.connection_dj import  cursor_rows
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from xulpymoney.libxulpymoneytypes import eOperationType
from money.models import (
    Accounts, 
    Comment, 
    Concepts, 
    Dividends, 
    Investments, 
    Investmentsoperations, 
    Operationstypes, 
    Strategies, 
    balance_user_by_operationstypes, 
    get_investmentsoperations_totals_of_all_investments, 
    percentage_to_selling_point, total_balance, 
    currencies_in_accounts, 
    qs_investments_netgains_usercurrency_in_year_month, 
    money_convert, 
)
from money.reusing.datetime_functions import dtaware_month_end
from money.reusing.percentage import percentage_between, Percentage
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count



def listdict_accounts(queryset):    
    
    list_=[]
    for account in queryset:
        balance=account.balance(timezone.now())
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
            t_io,  t_io_current, t_io_historical=investment.get_investmentsoperations_totals(dt, local_currency)
            basic_quotes=investment.products.basic_results()
            try:
                daily_diff=(basic_quotes['last']-basic_quotes['penultimate'])*t_io_current["shares"]*investment.products.real_leveraged_multiplier()
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
                    "invested_local": t_io_current["invested_user"], 
                    "balance": t_io_current["balance_user"], 
                    "gains": t_io_current["gains_gross_user"],  
                    "percentage_invested": Percentage(t_io_current["gains_gross_user"], t_io_current["invested_user"]), 
                    "percentage_sellingpoint": percentage_to_selling_point(t_io_current["shares"], investment.selling_price, basic_quotes['last']), 
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

def listdict_banks(queryset, dt, active, local_currency):
    list_=[]
    
    investments_totals_all_investments=get_investmentsoperations_totals_of_all_investments(dt, local_currency)
    for bank in queryset:
        accounts_balance=Accounts.accounts_balance_user_currency(bank.accounts(active), timezone.now())
        investments_balance =0
        for investment in bank.investments(active):
            investments_balance=investments_balance+investments_totals_all_investments[str(investment.id)]["io_current"]["balance_user"]
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
def listdict_product_quotes_month_comparation(product, ohclmonthly=None):
        if ohclmonthly is None:
            ohclmonthly=product.ohclMonthlyBeforeSplits()
            
        data=[]
        data
        minyear=ohclmonthly[0].year
        for i, year in enumerate(range(minyear,  date.today().year+1)):
            row=[]
            row.append(year)
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
                pass
#            for month in range(1, 13):
#                row.append(self.product.result.ohclMonthly.percentage_by_year_month(year, month))
#            row.append(self.product.result.ohclYearly.percentage_by_year(year))
#            data.append(row)
#            
#        self.mqtwMensuales.setData(
#            [self.tr("Year"), self.tr("January"),  self.tr("February"), self.tr("March"), self.tr("April"), self.tr("May"), self.tr("June"), self.tr("July"), self.tr("August"), self.tr("September"), self.tr("October"), self.tr("November"), self.tr("December"), self.tr("Total")], 
#            None, 
#            data, 
#            decimals=2, 
#            zonename=self.mem.localzone_name
#        )

## Gets all ioh from all investments 
def listdict_investmentsoperationshistorical(year, month, local_currency, local_zone):
    #Git investments with investmentsoperations in this year, month
    list_ioh=[]
    dict_ot=Operationstypes.dictionary()
    dt_year_month=dtaware_month_end(year, month, local_zone)
    for investment in Investments.objects.raw("select distinct(investments.*) from investmentsoperations, investments where date_part('year', datetime)=%s and date_part('month', datetime)=%s and investments.id=investmentsoperations.investments_id", (year, month)):
        io, io_current, io_historical=investment.get_investmentsoperations(dt_year_month, local_currency)
        
        for ioh in io_historical:
            if ioh['dt_end'].year==year and ioh['dt_end'].month==month:
                ioh["name"]=investment.fullName()
                ioh["operationstypes"]=dict_ot[ioh["operationstypes_id"]]
                ioh["years"]=0
                list_ioh.append(ioh)
    list_ioh= sorted(list_ioh,  key=lambda item: item['dt_end'])
    return list_ioh
    
    
## Gets all ioh from all investments 
def listdict_investmentsoperationscurrent_homogeneus_merging_same_product(product, account, dt, basic_results, local_currency, local_zone):
    #Git investments with investmentsoperations in this year, month
    list_ioc=[]
    dict_ot=Operationstypes.dictionary()
    for investment in Investments.objects.raw("select distinct(investments.*) from investmentsoperations, investments where datetime <=%s and investments.products_id=%s and investments.accounts_id=%s and investments.id=investmentsoperations.investments_id", (dt,  product.id, account.id)):
        io, io_current, io_historical=investment.get_investmentsoperations(dt, local_currency)
        
        for ioc in io_current:
            ioc["name"]=investment.fullName()
            ioc["operationstypes"]=dict_ot[ioc["operationstypes_id"]]
            ioc["percentage_annual"]=Investmentsoperations.investmentsoperationscurrent_percentage_annual(ioc, basic_results)
            ioc["percentage_apr"]=Investmentsoperations.investmentsoperationscurrent_percentage_apr(ioc)
            ioc["percentage_total"]=Investmentsoperations.investmentsoperationscurrent_percentage_total(ioc)
            ioc["operationstypes"]=dict_ot[ioc["operationstypes_id"]]
            list_ioc.append(ioc)
    return list_ioc


def listdict_products_pairs_evolution(product_worse, product_better, datetimes, ioc_worse, ioc_better, basic_results_worse,   basic_results_better):
    l=[]
    first_price_better=money_convert(ioc_better[0]["datetime"], ioc_better[0]["price_investment"], product_better.currency, product_worse.currency)
    for i in range(len(ioc_better)):
        price_better=money_convert(ioc_better[i]["datetime"], ioc_better[i]["price_investment"], product_better.currency, product_worse.currency)
        percentage_year_worse=percentage_between(ioc_worse[0]["price_investment"], ioc_worse[i]["price_investment"])
        percentage_year_better=percentage_between(first_price_better, price_better)
        l.append({
            "datetime":ioc_better[i ]["datetime"], 
            "price_worse": ioc_worse[i]["price_investment"], 
            "price_better": price_better, 
            "price_ratio":ioc_worse[i]["price_investment"]/price_better, 
            "percentage_year_worse": percentage_year_worse, 
            "percentage_year_better": percentage_year_better, 
            "percentage_year_diff": percentage_year_worse-percentage_year_better, 
        })
    price_better=money_convert(timezone.now(), basic_results_better["last"], product_better.currency, product_worse.currency)
    percentage_year_worse=percentage_between(ioc_worse[0]["price_investment"], basic_results_worse["last"]) 
    percentage_year_better=percentage_between(first_price_better, price_better)
    l.append({
        "datetime":timezone.now(), 
        "price_worse": basic_results_worse["last"], 
        "price_better": price_better, 
        "price_ratio": basic_results_worse["last"]/price_better, 
        "percentage_year_worse": percentage_year_worse, 
        "percentage_year_better": percentage_year_better, 
        "percentage_year_diff": percentage_year_worse-percentage_year_better, 
    })
    l= sorted(l,  key=lambda item: item['datetime'])
    return l

def listdict_products_pairs_evolution_from_datetime(product_worse, product_better, common_quotes, basic_results_worse,   basic_results_better):
    l=[]
    last_diff=Percentage(0, 1)
    first_a=common_quotes[0]["a_open"]
    first_b=common_quotes[0]["b_open"]
    for row in common_quotes:#a worse, b better
        percentage_year_worse=percentage_between(first_a,  row["a_open"])
        percentage_year_better=percentage_between(first_b, row["b_open"])
        diff=percentage_year_worse- percentage_year_better
        diff_before=diff-last_diff
        l.append({
            "datetime": row["date"], 
            "price_worse": row["a_open"], 
            "price_better": row["b_open"], 
            "price_ratio": row["a_open"]/row["b_open"], 
            "percentage_year_worse": percentage_year_worse, 
            "percentage_year_better": percentage_year_better, 
            "percentage_year_diff": diff, 
            "percentage_month_diff": diff_before
        })
        last_diff=diff
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
    with ThreadPoolExecutor(max_workers=cpu_count()+1) as executor:
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
    with ThreadPoolExecutor(max_workers=cpu_count()+1) as executor:
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
    last_month=last_year_balance 
    for future in futures:
        month_end, month_name,  total = future.result()
        list_.append({
            "month_number":month_end, 
            "month": month_name,
            "account_balance":total['accounts_user'], 
            "investment_balance":total['investments_user'], 
            "total":total['total_user'] , 
            "percentage_year": percentage_between(last_year_balance, total['total_user'] ), 
            "diff_lastmonth": total['total_user']-last_month, 
        })
        last_month=total['total_user']
    
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

    
def listdict_strategies(active, local_currency, local_zone):
    l=[]
    strategies=Strategies.objects.all().filter(dt_to__isnull=active)
    for strategy in strategies:
        gains_net_current=0
        gains_net_historical=0
        dividends_net=0
        
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
