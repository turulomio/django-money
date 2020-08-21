## @package admin
## @brief Defines everything for Django Admin Site

## Se mete en books  porque necesita los modelos


from django.utils.translation import ugettext_lazy as _
from money.models import Bank
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse_lazy
from django.contrib import admin# Need to import this since auth models get registered on import.


class BankAdmin(admin.ModelAdmin):
    model = Bank
    list_display = ['name','active']
    search_fields = ['name', 'active']


admin.site.site_title = _('Django money')
admin.site.site_header = _('Django money')
admin.site.index_title = _('My Django money administration')

admin.site.register(Bank)
    
admin.site.site_url = reverse_lazy('home') 
admin.site.logout_template=reverse_lazy('home')
