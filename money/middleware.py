from money import __version__, __versiondate__
from money.models import Globals
from money.reusing.currency import currency_symbol
from money.templatetags.mymenu import Menu, Action,  Group
from django.utils.translation import gettext_lazy as _
import time

## FOR VIEWS AND TEMPLATES
class MoneyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        start=time.time()
        self.menu=Menu(_("Django Money"))
        self.menu.append(Action(_("Banks"), None,  "bank_list_active",  True))
        self.menu.append(Action(_("Accounts"), None,  "account_list_active",  True))
        self.menu.append(Action(_("Investments"), None,  "investment_list_active",  True))
        self.menu.append(Action(_("Orders"), None,  "order_list_active",  True))
        grReport=Group(1, _("Reports"), "10",  True)
        grReport.append(Action(_("Concepts"), None, "report_concepts", True))
        grReport.append(Action(_("Total"), None, "report_total", True))
        grAdministration=Group(1, _("Management"), "20",  True)
        grAdministration.append(Action(_("Concepts"), None, "concept_list", True))
        
        grProducts=Group(1, _("Products"), "30",  True)
        grProducts.append(Action(_("Search"), None, "product_list", True))
#        grProductsPredefined=Group(1, _("Predefined"), "40", True)
#        grProductsPredefined.append(Action(_("Favorites"), None, "product_list", True))
#        grProducts.append(grProductsPredefined)
        
        self.menu.append(grProducts)
        self.menu.append(grReport)
        self.menu.append(grAdministration)
        print(_("Menu loaded in {}".format(time.time()-start)))

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
    
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        start=time.time()
        request.VERSION=__version__
        request.VERSIONDATE=__versiondate__
        request.menu=self.menu
        globals=Globals.objects.all()
        request.globals={}
        for g in globals:
            request.globals[g.global_field]=g.value
        request.local_currency_symbol=currency_symbol(request.globals["mem/localcurrency"])
        print(time.time()-start)
