from money import __version__, __versiondate__
from money.models import Globals
from money.reusing.currency import currency_symbol

import time

## FOR VIEWS AND TEMPLATES
class MoneyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

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
        globals=Globals.objects.all()
        request.globals={}
        for g in globals:
            request.globals[g.global_field]=g.value
        request.local_currency_symbol=currency_symbol(request.globals["mem/localcurrency"])
        print(time.time()-start)
