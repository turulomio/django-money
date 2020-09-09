from money.tabulator import TabulatorFromListDict, TabulatorFromQuerySet
from django.utils.translation import ugettext_lazy as _


class TabulatorAccounts(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "active", "number", "balance", "balance_user")
        self.setHeaders("Id", _("Name"), _("Active"), _("Number"), _("Balance"), _("Local curr. B."))
        self.setTypes("int","str", "bool", "str", "str", local_currency)
        self.setBottomCalc(None, "sum", None, "sum", "sum", "sum", None, None, None)

#class TabulatorAccountOperations(TabulatorFromQuerySet):
#    def __init__(self, name, destiny_url, queryset, account, dt_initial, local_zone):
#        balance=float(account.balance( dt_initial)[0].amount)
#        print(balance)
#        TabulatorFromQuerySet.__init__(self, name)
#        self.setDestinyUrl(destiny_url)
#        self.setQuerySet(queryset)
#        self.setLocalZone(local_zone)
#        self.setCallByNames("id","datetime", "concepts.name","amount", "balance","comment")
#        self.setHeaders("Id", _("Date and time"), _("Concept"), _("Amount"),_("Balance"),  _("Comment"))
#        self.setTypes("int","datetime", "str", account.currency, account.currency,  "str")
#        self.generate_listdict()
#        for d in self.listdict:
#            balance=balance+d["amount"]
#            d["balance"]=balance


class TabulatorAccountOperations(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, currency,  local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLayout("fitDataStretch")
        self.setHeight("400px")
        self.setLayout("fitDataTable")
        self.setLocalZone(local_zone)
        self.setFields("id","datetime", "concepts","amount", "balance","comment")
        self.setHeaders("Id", _("Date and time"), _("Concept"), _("Amount"),_("Balance"),  _("Comment"))
        self.setTypes("int","datetime", "str", currency, currency,  "str")
        self.setBottomCalc(None,  None, None, "sum", None, None)

class TabulatorBanks(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "active", "accounts_balance", "investments_balance", "total_balance")
        self.setHeaders("Id", _("Name"), _("Active"), _("Accounts balance"), _("Investments balance"), _("Total balance"))
        self.setTypes("int","str", "bool", local_currency,  local_currency, local_currency)
        self.setBottomCalc(None,  None, None, "sum", "sum", "sum")

class TabulatorConcepts(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "name", "operationstypes", "editable")
        self.setHeaders(_("Id"), _("Name"), _("Operation type"), _("Editable"))
        self.setTypes("int", "str", "str", "bool")
        self.generate_listdict()

class TabulatorInvestments(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, active, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLocalZone(local_zone)
        if active is True:
            self.setFields("id","name", "last_datetime","last_quote","daily_difference", "daily_percentage", "invested_local",  "balance", "gains", "percentage_invested", "percentage_sellingpoint")
            self.setHeaders(_("Id"), _("Name"), _("Last dt.") ,  _("Last quote"), _("Daily diff"), _("% daily"), _("Invested"),_("Balance"),  _("Gains"), _("% Invested"), _("% selling point"))
        else:
            self.setFields("id","name")
            self.setHeaders(_("Id"), _("Name"))
        self.setTypes("int", "str", "str", "float",  local_currency, "percentage", local_currency, local_currency, local_currency,"percentage", "percentage")
        self.setBottomCalc(None, None, None, None,"sum", None, "sum", "sum", "sum", None, None)
        self.setInitialOptions("""
    initialSort:[
    {column:"gains", dir:"desc"}, //then sort by this second
    {column:"percentage_sellingpoint", dir:"asc"}, //sort by this first
    ],""")

class TabulatorInvestmentsOperationsCurrentHomogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","datetime", "operationstypes",  "shares", "price_investment", "invested_investment", "balance_investment", "gains_gross_investment", "percentage_annual", "percentage_apr", "percentage_total")
        self.setHeaders("Id", _("Date and time"), _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
        self.setTypes("int","datetime", "str",  "Decimal", investment.products.currency, investment.products.currency, investment.products.currency,  investment.products.currency, "percentage", "percentage", "percentage")
        self.setBottomCalc(None, None, None, None, None, "sum", "sum", "sum", None, None, None)

class TabulatorInvestmentsOperationsCurrentHeterogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","datetime", "name",  "operationstypes",  "shares", "price_investment", "invested_investment", "balance_investment", "gains_gross_investment", "percentage_annual", "percentage_apr", "percentage_total")
        self.setHeaders("Id", _("Date and time"), _("Name"),  _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
        self.setTypes("int","datetime", "str", "str",  "Decimal", local_currency, local_currency, local_currency,  local_currency, "percentage", "percentage", "percentage")
        self.setBottomCalc(None, None,  None, None, None, None, "sum", "sum", "sum", None, None, None)

class TabulatorInvestmentsOperationsHistoricalHomogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","dt_end", "years","operationstypes","shares", "gross_start_investment", "gross_end_investment", "gross_gains_investment", "commissions_account", "taxes_account", "net_gains_investment")
        self.setHeaders("Id", _("Date and time"), _("Years"), _("Operation type"),  _("Shares"), _("Gross start"), _("Gross end"), _("Gross gains"), _("Commissions"), _("Taxes"), _("Net gains"))
        self.setTypes("int","datetime", "int",  "str", "Decimal", investment.products.currency, investment.products.currency, investment.products.currency, investment.products.currency, investment.products.currency, investment.products.currency)
        self.setBottomCalc(None, None, None,None, None, "sum", "sum", "sum", "sum", "sum", "sum")

class TabulatorProducts(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id",  "code","name")
        self.setHeaders(_("Id"), _("Code"),  _("Name"))
        self.setTypes("int", "int","str")

class TabulatorProductsPairsEvolution(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("datetime", "price_ratio", "percentage_year_worse", "percentage_year_better", "percentage_year_diff")
        self.setHeaders(_("Date and time"), _("Price ratio"), _("% year worse"), _("% year better"), _("% year diff"))
        self.setTypes("datetime", "Decimal", "percentage", "percentage", "percentage")

class TabulatorInvestmentsOperationsHistoricalHeterogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","dt_end", "years", "name", "operationstypes","shares", "gross_start_user", "gross_end_user", "gross_gains_user", "commissions_user", "taxes_user", "net_gains_user")
        self.setHeaders("Id", _("Date and time"), _("Years"),_("Investment"), _("Operation type"),  _("Shares"), _("Gross start"), _("Gross end"), _("Gross gains"), _("Commissions"), _("Taxes"), _("Net gains"))
        self.setTypes("int","datetime", "int", "str",   "str", "Decimal", local_currency, local_currency, local_currency, local_currency, local_currency, local_currency)
        self.setBottomCalc(None, None, None, None, None, None, "sum", "sum", "sum", "sum", "sum", "sum")
        
class TabulatorInvestmentsOperationsHomogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","datetime", "operationstypes","shares", "price", "commission", "taxes")
        self.setHeaders("Id", _("Date and time"), _("Operation types"),  _("Shares"), _("Price"), _("Commission"), _("Taxes"))
        self.setTypes("int","datetime", "str","Decimal", investment.products.currency, investment.accounts.currency, investment.accounts.currency)
        self.setBottomCalc(None, None, None, "sum", None, "sum", "sum")
        
class TabulatorCreditCards(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset, account):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "name", "number", "deferred", "maximumbalance")
        self.setHeaders(_("Id"), _("Name"), _("Number"), _("Deferred pay"), _("Maximum balance"))
        self.setTypes("int", "str", "str", "bool", account.currency)
        self.generate_listdict()        

class TabulatorCreditCardsOperations(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset, creditcard, local_zone):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setLocalZone(local_zone)
        self.setCallByNames("id", "datetime", "concepts", "amount", "comment")
        self.setHeaders(_("Id"), _("Date and time"), _("Concept"), _("Amount"), _("Comment"))
        self.setTypes("int", "datetime","str", creditcard.accounts.currency, "str")
        self.setBottomCalc(None, None, None, "sum", None)        
        self.generate_listdict()

class TabulatorDividends(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLocalZone(local_zone)
        self.setFields("id", "datetime","concepts", "gross", "taxes", "commission", "net")
        self.setHeaders(_("Id"), _("Date and time"), _("Concept"), _("Gross"), _("Taxes"), _("Commission"), _("Net"))
        self.setTypes("int", "datetime","str", currency, currency, currency, currency)
        self.setBottomCalc(None, None, None, "sum", "sum", "sum", "sum")        

class TabulatorReportConcepts(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id", "name", "operationstypes","total","percentage_total",  "median")
        self.setHeaders(_("id"), _("Name"), _("Operation type"),  _("Total"), _("% total"),  _("Median"))
        self.setTypes("int","str", "str", local_currency, "percentage", local_currency)
        self.setBottomCalc(None, None, None,"sum", None, None)   
        self.setInitialOptions("""
    initialSort:[
    {column:"total", dir:"desc"}, //sort by this first
    ],""")        

class TabulatorOrders(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "date", "expiration", ("investments.fullName",()), "shares", "price", "executed")
        self.setHeaders(_("Id"), _("Date"),_("Expiration"), _("Investment"),  _("Shares"), _("Price"), _("Executed"))
        self.setTypes("int", "str", "str", "str",   "Decimal", "Decimal", "str")
        self.generate_listdict()
        

class TabulatorReportTotal(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLayout("fitColumns")
        self.setFields("month", "account_balance","investment_balance", "total", "diff_lastmonth", "percentage_year")
        self.setHeaders(_("Month"), _("Account balance"), _("Investment balance"), _("Total balance"), _("Last month diff"), _("% year to date"))
        self.setTypes("str","EUR", "EUR", "EUR", "EUR","percentage")
        self.showLastRecord(False)
        self.setBottomCalc(None, None, None, None, "sum", None)      
        

class TabulatorReportIncomeTotal(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url, destiny_type=2, new_tab=True)##Type=2 year, month as parameter in id in the form "year/month/"
        self.setListDict(listdict)
        self.setLayout("fitColumns")
        self.setFields("id","month", "incomes","expenses", "gains", "dividends", "total")
        self.setHeaders("Id", _("Month"), _("Incomes"), _("Expenses"), _("Net gains"), _("Net dividends"), _("Total"))
        self.setTypes("int","str","EUR", "EUR", "EUR", "EUR","EUR")
        self.setBottomCalc(None, None, "sum", "sum", "sum", "sum", "sum")
        self.showLastRecord(False)
        
        
