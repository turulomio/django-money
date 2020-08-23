from money import __version__, __versiondate__
from money.templatetags.mymenu import Menu, Action
from django.utils.translation import gettext_lazy as _

def my_context(request):
    menu=Menu(_("Django Money"))
    menu.append(Action(_("Home"), None,  "home"))
    menu.append(Action(_("Banks"), None,  "bank_list"))
    menu.append(Action(_("Accounts"), None,  "account_list"))
    menu.append(Action(_("Investments"), None,  "investment_list"))
    
    return {
        'VERSION': __version__, 
        'VERSIONDATE': __versiondate__, 
        'menu': menu, 
    }
