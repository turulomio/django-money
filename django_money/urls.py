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
from django.contrib import admin
from django.urls import path
from django.conf.urls.i18n import i18n_patterns, set_language 
from django.contrib.auth.views import LoginView, logout_then_login

from money import views as money_views

urlpatterns = i18n_patterns(
    path('i18n/setlang/',  set_language, name="set_language"), 
    path('admin/', admin.site.urls,  name="admin-site"),
#    path('money/', money.urls, name="money-site"),
    path('', money_views.home, name='home'),
    
    path('signup/', money_views.signup, name='signup'),
    
    path('account_activation_sent/', money_views.account_activation_sent, name='account_activation_sent'),
    path('activate/(<uidb64>/<token>/',  money_views.activate, name='activate'),
    
    path('login/', LoginView.as_view(template_name='login.html'), name="login"), 
    path('logout/', logout_then_login, name="logout"), 
    
    path('bank/list/', money_views.bank_list, name='bank_list'),
    path('bank/view/<slug:pk>/', money_views.bank_list, name='bank_view'),
    path('bank/new/', money_views.bank_new, name='bank_new'),
    path('bank/update/<slug:pk>', money_views.bank_update, name='bank_update'),
    path('bank/delete/<slug:pk>', money_views.bank_delete, name='bank_delete'),


)

handler403 = 'money.views.error_403'