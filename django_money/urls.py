"""django_money URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from datetime import date
from django.contrib import admin
from django.urls import path
from django.conf.urls.i18n import i18n_patterns, set_language 
from django.contrib.auth.views import LoginView, logout_then_login
from django.views.generic.base import RedirectView

from money import views as money_views

urlpatterns=[
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]
urlpatterns=urlpatterns+ i18n_patterns(
    path('i18n/setlang/',  set_language, name="set_language"), 
    path('admin/', admin.site.urls,  name="admin-site"),
    path('', money_views.home, name='home'),
    
    path('login/', LoginView.as_view(template_name='login.html'), name="login"), 
    path('logout/', logout_then_login, name="logout"), 
    
    path('bank/list/', money_views.bank_list,  {'active':True}, name='bank_list_active'),
    path('bank/list/inactive/', money_views.bank_list,  {'active':False}, name='bank_list_inactive'),
    path('bank/view/<slug:pk>/', money_views.bank_view, name='bank_view'),
    path('bank/new/', money_views.bank_new, name='bank_new'),
    path('bank/update/<slug:pk>', money_views.bank_update.as_view(), name='bank_update'),
    path('bank/delete/<slug:pk>', money_views.bank_delete, name='bank_delete'),

    path('account/list/', money_views.account_list,   {'active':True}, name='account_list_active'),
    path('account/list/inactive/', money_views.account_list,   {'active':False}, name='account_list_inactive'),
    path('account/view/<slug:pk>/<int:year>/<int:month>/', money_views.account_view, name='account_view'),
    path('account/view/<int:pk>/', money_views.account_view, name='account_view'),
    path('account/transfer/<int:origin>/', money_views.account_transfer, name='account_transfer'),
    path('account/transfer/delete/<str:comment>/', money_views.account_transfer_delete, name='account_transfer_delete'),
    
    path('accountoperation/new/<int:accounts_id>/', money_views.accountoperation_new.as_view(), name='accountoperation_new'),
    path('accountoperation/update/<int:pk>/', money_views.accountoperation_update.as_view(), name='accountoperation_update'),
    path('accountoperation/delete/<int:pk>', money_views.accountoperation_delete.as_view(), name='accountoperation_delete'),
    
    
    path('creditcard/view/<slug:pk>/', money_views.creditcard_view, name='creditcard_view'),
    path('creditcard/new/<int:accounts_id>/', money_views.creditcard_new.as_view(), name='creditcard_new'),
    path('creditcard/update/<slug:pk>/', money_views.creditcard_update.as_view(), name='creditcard_update'),
    path('creditcard/delete/<slug:pk>/', money_views.creditcard_delete.as_view(), name='creditcard_delete'),
    
    
    path('creditcardoperation/new/<int:creditcards_id>', money_views.creditcardoperation_new.as_view(), name='creditcardoperation_new'),
    path('creditcardoperation/update/<int:pk>', money_views.creditcardoperation_update.as_view(), name='creditcardoperation_update'),
    path('creditcardoperation/delete/<int:pk>', money_views.creditcardoperation_delete.as_view(), name='creditcardoperation_delete'),

    path('investment/list/', money_views.investment_list, {'active':True}, name='investment_list_active'),
    path('investment/list/inactive/', money_views.investment_list, {'active': False}, name='investment_list_inactive'),
    path('investment/view/<slug:pk>/', money_views.investment_view, name='investment_view'),
    path('investment/update/<int:pk>', money_views.investment_update.as_view(), name='investment_update'),
    
    path('investment/pairs/<int:worse>/<int:better>/<int:accounts_id>/', money_views.investment_pairs, name='investment_pairs'),
    path('investment/pairs/<int:worse>/<int:better>/<int:accounts_id>/<int:amount>/', money_views.ajax_investment_pairs_invest, name='ajax_investment_pairs_invest'),
    path('investment/pairs/evolution/<int:worse>/<int:better>/', money_views.ajax_investment_pairs_evolution, name='ajax_investment_pairs_evolution'),
    
    path('investmentoperation/new/<int:investments_id>/', money_views.investmentoperation_new.as_view(), name='investmentoperation_new'),
    path('investmentoperation/update/<int:pk>', money_views.investmentoperation_update.as_view(), name='investmentoperation_update'),
    path('investmentoperation/delete/<int:pk>', money_views.investmentoperation_delete.as_view(), name='investmentoperation_delete'),
        
        
        
    path('order/list/', money_views.order_list, {'active':True}, name='order_list_active'),
    path('order/list/inactive/', money_views.order_list, {'active': False}, name='order_list_inactive'),
    path('order/view/<slug:pk>/', money_views.bank_view, name='order_view'),
    
    path('product/view/<slug:pk>/', money_views.product_view, name='product_view'),
    path('product/list/', money_views.product_list,  name='product_list'),
    path('product/list/favorites/', money_views.product_list_favorites,  name='product_list_favorites'),
    path('product/product_update/', money_views.product_update,  name='product_update'),
    
    path('quote/new/<int:products_id>/', money_views.quote_new.as_view(), name='quote_new'),
    
    path('concept/list/', money_views.concept_list,  name='concept_list'),
    
    path('chart/total/', money_views.ajax_chart_total, {'year_from': date.today().year},  name='ajax_chart_total'),
    path('chart/total/<int:year_from>/', money_views.ajax_chart_total,  name='ajax_chart_total'),
    
    path('report/concepts/',  money_views.report_concepts,  name='report_concepts'), 
    path('report/concepts/<int:year>/<int:month>/',  money_views.report_concepts,  name='report_concepts'), 
    path('report/total/', money_views.report_total,  name='report_total'),
    path('report/total/<int:year>/', money_views.report_total,  name='report_total'),
    path('report/total/div/income/<int:year>/', money_views.ajax_report_total_income,  name='ajax_report_total_income'),
    path('report/total/income/details/', money_views.report_total_income_details,  name='report_total_income_details'),
    path('report/total/income/details/<int:year>/<int:month>/', money_views.report_total_income_details,  name='report_total_income_details'),
    path('report/total/gainsbyproducttype/<int:year>/', money_views.ajax_report_gains_by_product_type,  name='ajax_report_gains_by_product_type'),
    
    path('strategy/list/', money_views.strategy_list, {'active':True}, name='strategy_list_active'),
    path('strategy/list/inactive/', money_views.strategy_list, {'active': False}, name='strategy_list_inactive'),
    
    
)

handler403 = 'money.views.error_403'
