from money.connection_dj import cursor_one_field
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from money.reusing.datetime_functions import dtaware_month_end, string2dtnaive, dtaware
from xulpymoney.libxulpymoneytypes import eOperationType
from money.otherstuff import balance_user_by_operationstypes, netgains_dividends, money_convert, get_investmentsoperations_totals_of_all_investments, total_balance, percentage_to_selling_point
from money.reusing.percentage import percentage_between, Percentage
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count


def qs_list_of_ids(qs):
    r=[]
    for o in qs:
        r.append(o.id)
    return tuple(r)

def qs_accounts_tabulator(queryset):    
    
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

def qs_investments_tabulator(queryset, dt,  local_currency, active):
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
    
def qs_accounts_balance_user(qs, dt):
    return cursor_one_field("select sum((account_balance(accounts.id,%s,'EUR')).balance_user_currency) from  accounts where id in %s", (dt, qs_list_of_ids(qs)))
    
def qs_banks_tabulator(queryset, dt, active, local_currency):
    list_=[]
    
    investments_totals_all_investments=get_investmentsoperations_totals_of_all_investments(dt, local_currency)
    for bank in queryset:
        accounts_balance=qs_accounts_balance_user(bank.accounts(active), timezone.now())
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


def qs_total_report_tabulator(qs_investments, qs_accounts, year, last_year_balance, local_currency, local_zone):
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
#            
#        for future in as_completed(futures): 
#            #print(future, future.result())

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
    

def qs_total_report_income_tabulator(qs_investments, qs_accounts, year, last_year_balance, local_currency, local_zone):
    def month_results(year,  month, month_name):
        dividends=netgains_dividends(year, month)
        incomes=balance_user_by_operationstypes(year,  month,  eOperationType.Income, local_currency, local_zone)-dividends
        expenses=balance_user_by_operationstypes(year,  month,  eOperationType.Expense, local_currency, local_zone)
        
        start=timezone.now()
        gains=qs_investments_netgains_usercurrency_in_year_month(qs_investments, year, month, local_currency)
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
    
def qs_investments_netgains_usercurrency_in_year_month(qs_investments, year, month, local_currency):
    r =0
    for investment in qs_investments:
        io, io_current, io_historical=investment.get_investmentsoperations(timezone.now(), 'EUR')
        for ioh in io_historical:
            if ioh['dt_end'].year==year and ioh['dt_end'].month==month:
                if ioh['shares']>=0:
                    gross_product_currency=ioh['shares']*(ioh['sellprice_investment']-ioh['buyprice_investment'])*investment.products.real_leveraged_multiplier()
                else:
                    gross_product_currency=ioh['shares']*(-ioh['sellprice_investment']+ioh['buyprice_investment'])*investment.products.real_leveraged_multiplier()
                gross_account_currency=money_convert(ioh['dt_end'], gross_product_currency, investment.products.currency, investment.accounts.currency)
                net_account_currency=gross_account_currency-ioh['taxes_account']-ioh['commissions_account']
                net_user_currency=money_convert(ioh['dt_end'], net_account_currency, investment.accounts.currency, local_currency)
                r=r+net_user_currency
    return r
