from django.utils.translation import ugettext_lazy as _
from money.reusing.currency import Currency
from money.reusing.datetime_functions import string2dtnaive, dtaware
from money.reusing.listdict_functions import listdict_sum
from money.reusing.percentage import Percentage
from money.tables import TabulatorFromListDict
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
    def __init__(self, request, investment,  str_ld_io, str_ld_io_current, str_ld_io_historical, name="IO"):
        self.request=request
        self.investment=investment
        self.name=name
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
        
    def current_shares(self):
        return listdict_sum(self.io_current, "shares")

    def current_invested_user(self):
        return listdict_sum(self.io_current, "invested_user")
        
    def current_average_price_account(self):
        """Calcula el precio medio de compra"""
        shares=self.current_shares()
        currency=self.investment.accounts.currency
        sharesxprice=Decimal(0)
        for o in self.io_current:
            sharesxprice=sharesxprice+o["shares"]*o["price_account"]
        return Currency(0, currency) if shares==Decimal(0) else Currency(sharesxprice/shares,  currency)

    def current_average_price_investment(self):
        """Calcula el precio medio de compra"""
        
        shares=self.current_shares()
        currency=self.investment.products.currency
        sharesxprice=Decimal(0)
        for o in self.io_current:
            sharesxprice=sharesxprice+o["shares"]*o["price_investment"]
        return Currency(0, currency) if shares==Decimal(0) else Currency(sharesxprice/shares,  currency)
        
    def current_gains_net_user(self):
        return listdict_sum(self.io_current, "gains_net_user")

    def current_gains_gross_user(self):
        return listdict_sum(self.io_current, "gains_gross_user")
    
    def current_gains_gross_investment(self):
        return listdict_sum(self.io_current, "gains_gross_investment")

    def historical_gains_net_user_between_dt(self, dt_from, dt_to):
        r=0
        for o in self.io_historical:
            if dt_from<=o["dt_end"] and o["dt_end"]<=dt_to:
                r=r + o["gains_net_user"]
        return r
        
    ## @param listdict_ioc
    def current_gains_gross_investment_at_selling_price(self):
        #Get selling price gains
        if self.investment.selling_price in (None, 0):
            return None
        gains=0
        for o in self.io_current:
            gains=gains+o["shares"]*(self.investment.selling_price-o['price_investment'])*self.investment.products.real_leveraged_multiplier()
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
        
                
    def current_tabulator_homogeneus_investment(self):
        r=TabulatorFromListDict(f"{self.name}_current_tabulator_homogeneus_investment")
        r.setDestinyUrl(None)
        r.setLocalZone(self.request.local_zone)
        r.setListDict(self.current_listdict_tabulator_homogeneus(self.request))
        r.setFields("id","datetime", "operationstypes",  "shares", "price_investment", "invested_investment", "balance_investment", "gains_gross_investment", "percentage_annual", "percentage_apr", "percentage_total")
        r.setHeaders("Id", _("Date and time"), _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
        r.setTypes("int","datetime", "str",  "Decimal", self.investment.products.currency, self.investment.products.currency, self.investment.products.currency,  self.investment.products.currency, "percentage", "percentage", "percentage")
        r.setBottomCalc(None, None, None, "sum", None, "sum", "sum", "sum", None, None, None)
        r.showLastRecord(False)
        
        r.setHTMLCodeAfterObjectCreation(f"""
    <p>{_("Current average price is {} in investment currency").format(self.current_average_price_investment())}</p>
""")
        return r        

    def o_tabulator_homogeneus_investment(self):
        r=TabulatorFromListDict(f"{self.name}_o_tabulator_homogeneus_investment")
        r.setDestinyUrl("investmentoperation_update")
        r.setLocalZone(self.request.local_zone)
        r.setListDict(self.o_listdict_tabulator_homogeneus(self.request))
        r.setFields("id","datetime", "operationstypes","shares", "price", "commission", "taxes")
        r.setHeaders("Id", _("Date and time"), _("Operation types"),  _("Shares"), _("Price"), _("Commission"), _("Taxes"))
        r.setTypes("int","datetime", "str","Decimal", self.investment.products.currency, self.investment.accounts.currency, self.investment.accounts.currency)
        r.setBottomCalc(None, None, None, "sum", None, "sum", "sum")
        r.showLastRecord(False)
        return r

    def historical_tabulator_homogeneus_investment(self):
        r=TabulatorFromListDict(f"{self.name}_historical_tabulator_homogeneus_investment")
        r.setDestinyUrl(None)
        r.setLocalZone(self.request.local_zone)
        r.setListDict(self.historical_homogeneus_listdict_tabulator(self.request))
        r.setFields("id","dt_end", "years","operationstypes","shares", "gross_start_investment", "gross_end_investment", "gains_gross_investment", "commissions_account", "taxes_account", "gains_net_investment")
        r.setHeaders("Id", _("Date and time"), _("Years"), _("Operation type"),  _("Shares"), _("Gross start"), _("Gross end"), _("Gross gains"), _("Commissions"), _("Taxes"), _("Net gains"))
        r.setTypes("int","datetime", "int",  "str", "Decimal", self.investment.products.currency, self.investment.products.currency, self.investment.products.currency, self.investment.products.currency, self.investment.products.currency, self.investment.products.currency)
        r.setBottomCalc(None, None, None,None, None, "sum", "sum", "sum", "sum", "sum", "sum")
        r.showLastRecord(False)
        return r

    def historical_homogeneus_listdict_tabulator(self, request):
        for ioh in self.io_historical:
            ioh["operationstypes"]=request.operationstypes[ioh["operationstypes_id"]]
            ioh["years"]=0
        return self.io_historical
        
        
    ## Gets and investment operation from its listdict_io using an id
    ## @param id integer with the id of the investment operation
    def o_find_by_id(self,  id):
        for o in self.io:
            if o["id"]==id:
                return o

def InvestmentsOperations_from_investment(request,  investment, dt, local_currency):
    row_io= cursor_one_row("select * from investment_operations(%s,%s,%s)", (investment.pk, dt, local_currency))
    r=InvestmentsOperations(request, investment,  row_io["io"], row_io['io_current'],  row_io['io_historical'])
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
        
    def LdoInvestmentsOperationsCurrentHeterogeneus_between(self, dt_from, dt_to):
        from money.listdict import LdoInvestmentsOperationsCurrentHeterogeneus
        r=LdoInvestmentsOperationsCurrentHeterogeneus(self.request)
        for io in self.list:
            for o in io.io_current:
                if dt_from<=o["datetime"] and o["datetime"]<=dt_to:
                    o["name"]=io.investment.fullName()
                    o["operationstypes"]=self.request.operationstypes[o["operationstypes_id"]]
                    r.append(o)
        r.order_by("datetime")
        return r
        
    def LdoInvestmentsOperationsHistoricalHeterogeneus_between(self, dt_from, dt_to):
        from money.listdict import LdoInvestmentsOperationsHistoricalHeterogeneus
        r=LdoInvestmentsOperationsHistoricalHeterogeneus(self.request)
        for io in self.list:
            for o in io.io_historical:
                if dt_from<=o["dt_end"] and o["dt_end"]<=dt_to:
                    o["name"]=io.investment.fullName()
                    o["operationstypes"]=self.request.operationstypes[o["operationstypes_id"]]
                    r.append(o)
        r.order_by("dt_end")
        return r

## Generate object from and ids list
def InvestmentsOperationsManager_from_investment_queryset(qs_investments, dt, request):
    r=InvestmentsOperationsManager(request)
    for investment in qs_investments:
        r.append(InvestmentsOperations_from_investment(request, investment, dt, request.local_currency))
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
        
    def find_by_id(self, id):
        for o in self.list:
            if o.investment.id==id:
                return o
        return None
        

## Generate object from and ids list
def InvestmentsOperationsTotalsManager_from_investment_queryset(qs_investments, dt, request):
    r=InvestmentsOperationsTotalsManager(request)
    for investment in qs_investments:
        r.append(InvestmentsOperationsTotals_from_investment(investment, dt, request.local_currency))
    return r
    
def InvestmentsOperationsTotalsManager_from_all_investments(request, dt):
    from money.models import Investments
    qs=Investments.objects.all()
    return InvestmentsOperationsTotalsManager_from_investment_queryset(qs, dt, request)
    
## Manage output of  investment_operation_alltotals is one row
class InvestmentsOperationsAllTotals:
    def __init__(self, only_active):
        pass
        
        
        
## Manage output of  total balance on one row accounts, and investment totals
class TotalBalance:
    def __init__(self, str_d_io_total, str_d_io_current_total, str_d_io_historical_total):
        pass
