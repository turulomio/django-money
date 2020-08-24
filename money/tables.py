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
        

class TabulatorInvestments(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset, local_currency):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", ("fullName", ()), "active", ("invested",()),("gains",()))
        self.setHeaders(_("Id"), _("Name"), _("Active"), _("Invested"), _("Gains"))
        self.setTypes("int", "str", "bool", local_currency, local_currency)
        self.setBottomCalc(None, None, None, "sum", "sum")
        self.generate_listdict()

class TabulatorInvestmentsOperationsCurrent(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","datetime", "shares", "price", "price", "price", "price", "price", "price", "price")
        self.setHeaders("Id", _("Date and time"), _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Pending"), _("% year"), _("% APR"), _("% Total"))
        self.setTypes("int","datetime", "Decimal", investment.products.currency, investment.products.currency, investment.products.currency,  investment.products.currency, None, None, None)
        self.setBottomCalc(None, "sum", None, "sum", "sum", "sum", None, None, None)
        
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
        
