from money.reusing.currency import Currency
from money.reusing.datetime_functions import string2dtnaive, dtaware
from money.reusing.listdict_functions import listdict_sum
from money.reusing.percentage import Percentage
from datetime import date
from decimal import Decimal
Decimal

from money.connection_dj import cursor_one_row

## Converting dates to string in postgres functions return a string datetime instead of a dtaware. Here we convert it
def postgres_datetime_string_2_dtaware(s):
    str_dt_end=s[:19]            
    dt_end_naive=string2dtnaive(str_dt_end, "%Y-%m-%d %H:%M:%S")#Es un string desde postgres
    dt_end=dtaware(dt_end_naive.date(), dt_end_naive.time(), 'UTC')
    return dt_end

## Class to manage a single investment operation crrent
class IOC:
    def __init__(self, investment, d_ioc):
        self.investment=investment
        self.d=d_ioc
        
                
    def percentage_annual(self):
        if self.d["datetime"].year==date.today().year:
            lastyear=self.d["price_investment"] #Product value, self.money_price(type) not needed.
        else:
            lastyear=self.investment.products.basic_results()["lastyear"]
        if self.investment.products.basic_results()["lastyear"] is None or lastyear is None:
            return Percentage()

        if self.d["shares"]>0:
            return Percentage(self.investment.products.basic_results()["last"]-lastyear, lastyear)
        else:
            return Percentage(-(self.investment.products.basic_results()["last"]-lastyear), lastyear)

    def age(self):
            return (date.today()-self.d["datetime"].date()).days

    def percentage_apr(self):
            dias=self.age()
            if dias==0:
                dias=1
            return Percentage(self.percentage_total()*365,  dias)


    def percentage_total(self):
        if self.d["invested_investment"] is None:#initiating xulpymoney
            return Percentage()
        return Percentage(self.d['gains_gross_investment'], self.d["invested_investment"])


class IoManager:
    def __init__(self, request):
        self.request=request
        self.list=[]
        
    def append(self, o):
        self.list.append(o)

## Manage output of  investment_operations
class InvestmentsOperations:
    def __init__(self, investment,  str_ld_io, str_ld_io_current, str_ld_io_historical):
        self.investment=investment
        self.io=eval(str_ld_io)
        for o in self.io:
            o["datetime"]=postgres_datetime_string_2_dtaware(o["datetime"])
            
        self.io_current=eval(str_ld_io_current)
        for o in self.io_current:
            o["datetime"]=postgres_datetime_string_2_dtaware(o["datetime"])
           
        self.io_historical=eval(str_ld_io_historical)
        for o in self.io_historical:
            o["dt_start"]=postgres_datetime_string_2_dtaware(o["dt_start"])
            o["dt_end"]=postgres_datetime_string_2_dtaware(o["dt_end"])
        
    def current_gains_net_user(self):
        return listdict_sum(self.io_current, "gains_net_user")

    def current_gains_gross_user(self):
        return listdict_sum(self.io_current, "gains_gross_user")

    def historical_gains_net_user_between_dt(self, dt_from, dt_to):
        r=0
        for o in self.io_historical:
            if dt_from<=o["dt_end"] and o["dt_end"]<=dt_to:
                r=r + o["gains_net_user"]
        return r
        
    ## @param listdict_ioc
    def current_gains_gross_user_at_selling_price(self):
        #Get selling price gains
        if self.investment.selling_price is None:
            return None
        gains=0
        for o in self.io_current:
            gains=gains+abs(o["shares"]*(self.investment.selling_price-o['price_investment'])*self.investment.products.real_leveraged_multiplier())
        return Currency(gains, self.investment.products.currency)

    def o_listdict_tabulator_homogeneus(self, request):
        for o in self.io:
            o["operationstypes"]=request.operationstypes[o["operationstypes_id"]]
        return self.io        

    def current_listdict_tabulator_homogeneus(self, request):
        for ioc in self.io_current:
            o=IOC(self.investment, ioc)
            ioc["percentage_annual"]=o.percentage_annual()
            ioc["percentage_apr"]=o.percentage_apr()
            ioc["percentage_total"]=o.percentage_total()
            ioc["operationstypes"]=request.operationstypes[ioc["operationstypes_id"]]
        return self.io_current
        
    def historical_homogeneus_listdict_tabulator(self, request):
        for ioh in self.io_historical:
            ioh["operationstypes"]=request.operationstypes[ioh["operationstypes_id"]]
            ioh["years"]=0
        return self.io_historical
        
                
def InvestmentsOperations_from_investment( investment, dt, local_currency):
    row_io= cursor_one_row("select * from investment_operations(%s,%s,%s)", (investment.pk, dt, local_currency))
    r=InvestmentsOperations(investment,  row_io["io"], row_io['io_current'],  row_io['io_historical'])
    return r

## Set of InvestmentsOperations
class InvestmentsOperationsManager(IoManager):
    def __init__(self, request):
        IoManager.__init__(self, request)

    def current_gains_gross_user(self):
        r=0
        for o in self.list:
            r=r + o.current_gains_gross_user()
        return r

    def current_gains_net_user(self):
        r=0
        for o in self.list:
            r=r + o.current_gains_net_user()
        return r   
    
    def historical_gains_net_user_between_dt(self, dt_from, dt_to):
        r=0
        for o in self.list:
                r=r + o.historical_gains_net_user_between_dt(dt_from, dt_to)
        return r
        

## Generate object from and ids list
def InvestmentsOperationsManager_from_investment_queryset(qs_investments, dt, request):
    r=InvestmentsOperationsManager(request)
    for investment in qs_investments:
        r.append(InvestmentsOperations_from_investment(investment, dt, request.local_currency))
    return r
        
## Manage output of  investment_operation_totals on one row
class InvestmentsOperationsTotals:
    def __init__(self, investment, str_d_io_total, str_d_io_current_total, str_d_io_historical_total):
        self.investment=investment
        self.io_total=eval(str_d_io_total)
        self.io_total_current=eval(str_d_io_current_total)
        self.io_total_historical=eval(str_d_io_historical_total)
                
def InvestmentsOperationsTotals_from_investment( investment, dt, local_currency):
    row_io= cursor_one_row("select * from investment_operations_totals(%s,%s,%s)", (investment.pk, dt, local_currency))
    r=InvestmentsOperationsTotals(investment,  row_io["io"], row_io['io_current'],  row_io['io_historical'])
    return r
        
## Manage several rows of investment_operation_totals in several rows (list)
class InvestmentsOperationsTotalsManager(IoManager):
    def __init__(self, request):
        IoManager.__init__(self, request)
        
        
    def current_gains_gross_user(self):
        r=0
        for o in self.list:
            r=r + o.io_total_current["gains_gross_user"]
        return r   
        
    def current_gains_net_user(self):
        r=0
        for o in self.list:
            r=r + o.io_total_current["gains_net_user"]
        return r     

    def historical_gains_net_user(self):
        r=0
        for o in self.list:
            r=r + o.io_total_historical["gains_net_user"]
        return r
        

## Generate object from and ids list
def InvestmentsOperationsTotalsManager_from_investment_queryset(qs_investments, dt, request):
    r=InvestmentsOperationsTotalsManager(request)
    for investment in qs_investments:
        r.append(InvestmentsOperationsTotals_from_investment(investment, dt, request.local_currency))
    return r
    
## Manage output of  investment_operation_alltotals is one row
class InvestmentsOperationsAllTotals:
    def __init__(self, only_active):
        pass
        
        
        
## Manage output of  total balance on one row accounts, and investment totals
class TotalBalance:
    def __init__(self, str_d_io_total, str_d_io_current_total, str_d_io_historical_total):
        pass
