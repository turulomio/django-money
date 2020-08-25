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
    grAdministration=Group(1, _("Management"), "11",  True)
    grAdministration.append(Action(_("Concepts"), None, "concept_list", True))
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
