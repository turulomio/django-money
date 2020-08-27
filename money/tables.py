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
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "last_datetime","last_quote","daily_difference", "daily_percentage", "invested_local",  "balance", "gains", "percentage_invested", "percentage_sellingpoint")
        self.setHeaders(_("Id"), _("Name"), _("Last dt.") ,  _("Last quote"), _("Daily diff"), _("% daily"), _("Invested"),_("Balance"),  _("Gains"), _("% Invested"), _("% selling point"))
        self.setTypes("int", "str", "str", "float",  local_currency, "percentage", local_currency, local_currency, local_currency,"percentage", "percentage")
        self.setBottomCalc(None, None, None, None,"sum", None, "sum", "sum", "sum", None, None)

class TabulatorInvestmentsOperationsCurrent(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","datetime", "shares", "price", "price", "price", "price", "price", "price", "price")
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
        
class TabulatorInvestmentsOperations(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset, investment):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id","datetime", "shares", "price", "price", "price", "price", "price", "price", "price")
        self.setHeaders("Id", _("Date and time"), _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Pending"), _("% year"), _("% APR"), _("% Total"))
        self.setTypes("int","datetime", "Decimal", investment.products.currency, investment.products.currency, investment.products.currency,  investment.products.currency, None, None, None)
        self.setBottomCalc(None, "sum", None, "sum", "sum", "sum", None, None, None)
        self.generate_listdict()
        
class TabulatorCreditCards(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset, account):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "name", "number", "deferred", "maximumbalance")
        self.setHeaders(_("Id"), _("Name"), _("Number"), _("Deferred pay"), _("Maximum balance"))
        self.setTypes("int", "str", "str", "bool", account.currency)
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
