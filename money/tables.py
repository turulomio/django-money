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
                
class TabulatorAccountOperations(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset, account, dt_initial):
        balance=float(account.balance( dt_initial)[0].amount)
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id","datetime", "concepts.name","amount", "balance","comment")
        self.setHeaders("Id", _("Date and time"), _("Concept"), _("Amount"),_("Balance"),  _("Comment"))
        self.setTypes("int","datetime", "str", account.currency, account.currency,  "str")
        self.generate_listdict()
        for d in self.listdict:
            balance=balance+d["amount"]
            d["balance"]=balance

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
    def __init__(self, name, destiny_url, listdict, local_currency, active):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
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
    {column:"percentage_sellingpoint", dir:"asc"}, //sort by this first
    ],""")

class TabulatorInvestmentsOperationsCurrent(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","datetime", "shares", "price_investment", "invested_investment", "balance_investment", "gains_net_investment", "gains_net_investment", "gains_net_investment", "gains_net_investment")
        self.setHeaders("Id", _("Date and time"), _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Pending"), _("% year"), _("% APR"), _("% Total"))
        self.setTypes("int","datetime", "Decimal", investment.products.currency, investment.products.currency, investment.products.currency,  investment.products.currency, None, None, None)
        self.setBottomCalc(None, "sum", None, "sum", "sum", "sum", None, None, None)

class TabulatorInvestmentsOperationsHistorical(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","dt_end", "shares")
        self.setHeaders("Id", _("Date and time"), _("Shares"))
        self.setTypes("int","datetime", "Decimal")
        self.setBottomCalc(None, None, None,)
        
class TabulatorInvestmentsOperations(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","datetime", "shares", "price", "commission", "taxes")
        self.setHeaders("Id", _("Date and time"), _("Shares"), _("Price"), _("Commission"), _("Taxes"))
        self.setTypes("int","datetime", "Decimal", investment.products.currency, investment.accounts.currency, investment.accounts.currency)
        self.setBottomCalc(None, "sum", None, None, "sum", "sum")
        
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
    def __init__(self, name, destiny_url, queryset, creditcard):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "datetime", "concepts", "amount", "comment")
        self.setHeaders(_("Id"), _("Date and time"), _("Concept"), _("Amount"), _("Comment"))
        self.setTypes("int", "datetime","str", creditcard.accounts.currency, "str")
        self.setBottomCalc(None, None, None, "sum", None)        
        self.generate_listdict()

class TabulatorOrders(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "date", "expiration", ("investments.fullName",()), "shares", "price", "executed")
        self.setHeaders(_("Id"), _("Date"),_("Expiration"), _("Investment"),  _("Shares"), _("Price"), _("Executed"))
        self.setTypes("int", "str", "str", "str",   "Decimal", "Decimal", "str")
        self.generate_listdict()
        
        
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
class TabulatorReportTotal(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("month", "account_balance","investment_balance", "total", "diff_lastmonth", "percentage_year")
        self.setHeaders(_("Month"), _("Account balance"), _("Investment balance"), _("Total balance"), _("Last month diff"), _("% year to date"))
        self.setTypes("str","EUR", "EUR", "EUR", "EUR","percentage")
        self.setBottomCalc(None, None, None, None, "sum", None)      
        

class TabulatorReportIncomeTotal(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("month", "incomes","expenses", "gains", "dividends", "total")
        self.setHeaders(_("Month"), _("Incomes"), _("Expenses"), _("Net gains"), _("Net dividends"), _("Total"))
        self.setTypes("str","EUR", "EUR", "EUR", "EUR","EUR")
        self.setBottomCalc(None, "sum", "sum", "sum", "sum", "sum")
