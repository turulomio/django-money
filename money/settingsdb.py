from money.models import Globals
from money.reusing.currency import currency_symbol

def settingsdb(key):
    return Globals.objects.all().filter(global_field=key)[0].value
    
def settingsdb_currency_symbol(key):
    return currency_symbol(settingsdb(key))
    
def settingsdb_list(key):
    pass

