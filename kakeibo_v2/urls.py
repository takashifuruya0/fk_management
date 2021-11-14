# coding:utf-8
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from .views import views_kakeibo


app_name = 'kakeibo_v2'
urlpatterns = [
    path('', views_kakeibo.KakeiboTop.as_view(), name="kakeibo_top"),
    path('/create/income', views_kakeibo.KakeiboIncomeCreate.as_view(), name="kakeibo_income_create"),
    path('/create/expense', views_kakeibo.KakeiboExpenseCreate.as_view(), name="kakeibo_expense_create"),
    path('create/exchange', views_kakeibo.KakeiboExchangeCreate.as_view(), name="kakeibo_exchange_create"),
    path('create/transfer', views_kakeibo.KakeiboTransferCreate.as_view(), name="kakeibo_transfer_create"),
    # # autcomplete
    # path('autocomplete/usage', UsageAutocomplete.as_view(), name="autocomplete_usage"),
    # path('autocomplete/resource', ResourceAutocomplete.as_view(), name="autocomplete_resource"),    
]
