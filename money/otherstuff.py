from money.connection_dj import cursor_one_field, cursor_one_column, cursor_one_row, cursor_rows
from money.reusing.datetime_functions import dtaware_month_end
from decimal import Decimal
Decimal()


## Genera una fila (io, io_current, io_historical) con los totales de todas las inversiones
def get_investments_alltotals(dt, local_currency, only_active):
    row_io= cursor_one_row("select * from  investment_operations_alltotals( %s,%s,%s)", (dt, local_currency, only_active))
    io= eval(row_io["io"])
    current= eval(row_io['io_current'])
    historical= eval(row_io['io_historical'])
    return io,  current, historical
    
## Lista los id, io, io_current_totals, io_historical_current de todas las inversiones
## Devuelve un diccionario d[id][
##        investments_totals_all_investments=get_investmentsoperations_totals_of_all_investments(dt, local_currency)
## investments_totals_all_investments[str(investment.id)]["io_current"]["balance_user"]
def get_investmentsoperations_totals_of_all_investments(dt, local_currency):
    d={}
    for row in cursor_rows("select id, (investment_operations_totals(id, %s,%s)).io, (investment_operations_totals(id, %s, %s)).io_current, (investment_operations_totals(id, %s, %s)).io_historical from  investments;", (dt, local_currency, dt, local_currency, dt, local_currency)):
        d[str(row['id'])]={"io": eval(row['io']),"io_current": eval(row['io_current']),"io_historical": eval(row['io_historical']), }
    return d

def currencies_in_accounts():
    return cursor_one_column("select distinct(currency) from accounts")






def money_convert(dt, amount, from_,  to_):   
    return cursor_one_field("select * from money_convert(%s, %s, %s, %s)", (dt, amount, from_,  to_))

## This method should take care of diffrent currencies
def balance_user_by_operationstypes(year,  month,  operationstypes_id, local_currency, local_zone):
    r=0
    for currency in currencies_in_accounts():
        print(currency)
        balance=cursor_one_field("""
            select sum(amount) as amount 
            from 
                accountsoperations,
                accounts
            where 
                operationstypes_id={0} and 
                date_part('year',datetime)={1} and
                date_part('month',datetime)={2} and
                accounts.currency='{3}' and
                accounts.id=accountsoperations.accounts_id   
        union all 
            select sum(amount) as amount 
            from 
                creditcardsoperations ,
                creditcards,
                accounts
            where 
                operationstypes_id={0} and 
                date_part('year',datetime)={1} and
                date_part('month',datetime)={2} and
                accounts.currency='{3}' and
                accounts.id=creditcards.accounts_id and
                creditcards.id=creditcardsoperations.creditcards_id""".format(operationstypes_id, year, month,  currency))

        if balance is not None:
            r=r+money_convert(dtaware_month_end(year, month, local_zone), balance, currency, local_currency)
    return r

## TODO This method should take care of diffrent currencies in accounts. Dividens are in account currency
def net_dividends(year, month):
    dividends=cursor_one_field("""
select 
    sum(net) 
from 
    dividends 
where 
    date_part('year',datetime)=%s and
    date_part('month',datetime)=%s
""", (year, month))
    if dividends is None:
        dividends=0
    return dividends
    
    
    
    
