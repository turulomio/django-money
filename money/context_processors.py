from money import __version__, __versiondate__
from money.reusing.currency import currency_symbol
from money.settingsdb import settingsdb
from money.templatetags.mymenu import Menu, Action,  Group
from django.utils.translation import gettext_lazy as _

def my_context(request):
    menu=Menu(_("Django Money"))
    menu.append(Action(_("Banks"), None,  "bank_list_active",  True))
    menu.append(Action(_("Accounts"), None,  "account_list_active",  True))
    menu.append(Action(_("Investments"), None,  "investment_list_active",  True))
    menu.append(Action(_("Orders"), None,  "order_list_active",  True))
    grReport=Group(1, _("Reports"), "10",  True)
    grReport.append(Action(_("Concepts"), None, "report_concepts", True))
    grReport.append(Action(_("Total"), None, "report_total", True))
    grAdministration=Group(1, _("Management"), "20",  True)
    grAdministration.append(Action(_("Concepts"), None, "concept_list", True))
    grProducts=Group(1, _("Products"), "30",  True)
    grProducts.append(Action(_("Search"), None, "product_list", True))
    
    menu.append(grProducts)
    menu.append(grReport)
    menu.append(grAdministration)

    local_currency=settingsdb("mem/localcurrency")
    local_currency_symbol=currency_symbol(local_currency)
    
    return {
        'VERSION': __version__, 
        'VERSIONDATE': __versiondate__, 
        'menu': menu, 
        'local_currency': local_currency, 
        'local_currency_symbol': local_currency_symbol, 
    }
