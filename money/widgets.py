## Este modulo devuelve widgets entero para renderizar en las plantillas
## Si empieza por table es un tabulator
from django.utils.translation import ugettext_lazy as _
from money.reusing.listdict_functions import listdict_print_first
from money.reusing.tabulator import TabulatorFromListDict

def table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency(ld_ioc, local_zone, name="table_ioc_homogeneus_usercurrency"):      
    listdict_print_first(ld_ioc)
    currency=ld_ioc[0]["currency_user"]
    r=TabulatorFromListDict(name)
    r.setDestinyUrl(None)
    r.setLocalZone(local_zone)
    r.setListDict(ld_ioc)
    r.setFields("id","datetime", "name","operationstypes",  "shares", "price_user", "invested_user", "balance_user", "gains_gross_user", "percentage_annual", "percentage_apr", "percentage_total")
    r.setHeaders("Id", _("Date and time"), _("Name"),  _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
    r.setTypes("int","datetime", "str", "str",  "Decimal", currency, currency, currency, currency, "percentage", "percentage", "percentage")
    r.setBottomCalc(None, None, None, None, "sum", None,  "sum", "sum", "sum", None, None, None)
    r.showLastRecord(False)
    return r.render()
