from money.connection_dj import cursor_one_field, cursor_rows
from django.utils import timezone

from money.reusing.percentage import percentage_between, Percentage
def qs_list_of_ids(qs):
    r=[]
    for o in qs:
        r.append(o.id)
    return tuple(r)

def qs_investments_balance(qs):
#    return cursor_one_field("select sum((investment_totals(investments.id,now(),'EUR')).balance) from   investments where id in %s", (qs_list_of_ids(qs)))
    ## Crash al hacerlo así, sin embargo funciona con qs_accounts_balance_user, raro, sumo luego
    r =0
    for investment in qs:#("select (investment_totals(id, now(),'EUR')).balance from   investments where id in %s", (qs_list_of_ids(qs))):
        totals=investment.totals(timezone.now(), 'EUR')
        r=r+totals["balance"]
    return r

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
def qs_investments_tabulator(queryset, dt,  local_currency):    
    
    def percentage_to_selling_point(shares, selling_price, last_quote):       
        """Función que calcula el tpc selling_price partiendo de las el last y el valor_venta
        Necesita haber cargado mq getbasic y operinversionesactual"""
        if selling_price==0 or selling_price==None:
            return Percentage()
        if shares>0:
            return Percentage(selling_price-last_quote, last_quote)
        else:#Long short products
            return Percentage(-(selling_price-last_quote), last_quote)
    list_=[]
    for investment in queryset:
        totals=investment.totals(dt, local_currency)
        basic_quotes=investment.products.basic_results()
        list_.append({
                "id": investment.id, 
                "active":investment.active, 
                "name": investment.fullName(), 
                "last_datetime": basic_quotes['last_datetime'], 
                "last_quote": basic_quotes['last'], 
                "daily_difference":(basic_quotes['last']-basic_quotes['penultimate'])*totals['shares']*investment.products.real_leveraged_multiplier(), 
                "daily_percentage":percentage_between(basic_quotes['penultimate'], basic_quotes['last']), 
                "balance": totals["balance_local"], 
                "gains": totals["gains_local"], 
                "percentage_invested": Percentage(totals['gains'], totals['invested']), 
                "percentage_sellingpoint": percentage_to_selling_point(totals["shares"], investment.selling_price, basic_quotes['last']), 
                "invested_local": totals["invested_local"], 
                "deposit_local": totals["deposit_local"], 
            }
        )
    return list_
    
def qs_accounts_balance_user(qs, dt):
    print(qs_list_of_ids(qs))
    return cursor_one_field("select sum((account_balance(accounts.id,%s,'EUR')).balance_user_currency) from  accounts where id in %s", (dt, qs_list_of_ids(qs)))
    
def qs_banks_tabulator(queryset, dt, active):
    list_=[]
    for bank in queryset:
        accounts_balance=qs_accounts_balance_user(bank.accounts(active), timezone.now())
        #print(accounts_balance)
        investments_balance=qs_investments_balance(bank.investments(active))
        print(investments_balance)
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
