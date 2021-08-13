# coding:utf-8
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from kakeibo.views.views_kakeibo import KakeiboTop
from kakeibo.views.views_kakeibo import KakeiboList, KakeiboDetail, KakeiboCreate, KakeiboUpdate, KakeiboDelete
from kakeibo.views.views_kakeibo import EventList, EventCreate, EventUpdate, EventDetail, EventDelete
from kakeibo.views.views_kakeibo import ExchangeCreate
from kakeibo.views.views_autocomplete import UsageAutocomplete, ResourceAutocomplete
from kakeibo.views.views_shared import SharedTop, SharedList, SharedDetail, SharedCreate, SharedUpdate, SharedDelete
from kakeibo.views.views_shared import SharedResourceDetail, SharedResourceList, SharedResourceUpdate, SharedResourceCreate
from kakeibo.views.views_shared import SharedTransactionDetail,SharedTransactionUpdate
from kakeibo.views.views_shared import SharedTransactionCreate, SharedTransactionDelete
from kakeibo.views.views_credit import CreditImport, CreditLink, CreditLinkFromKakeibo

app_name = 'kakeibo'
urlpatterns = [
    # shared
    path('shared', SharedTop.as_view(), name="shared_top"),
    path('shared/list', SharedList.as_view(), name="shared_list"),
    path('shared/<int:pk>', SharedDetail.as_view(), name="shared_detail"),
    path('shared/<int:pk>/edit', SharedUpdate.as_view(), name="shared_update"),
    path('shared/<int:pk>/delete', SharedDelete.as_view(), name="shared_delete"),
    path('shared/create', SharedCreate.as_view(), name="shared_create"),
    path('shared/resource', SharedResourceList.as_view(), name="shared_resource_list"),
    path('shared/resource/create', SharedResourceCreate.as_view(), name="shared_resource_create"),
    path('shared/resource/<int:pk>', SharedResourceDetail.as_view(), name="shared_resource_detail"),
    path('shared/resource/<int:pk>/edit', SharedResourceUpdate.as_view(), name="shared_resource_update"),
    path('shared/transaction/create', SharedTransactionCreate.as_view(), name="shared_transaction_create"),
    path('shared/transaction/<int:pk>', SharedTransactionDetail.as_view(), name="shared_transaction_detail"),
    path('shared/transaction/<int:pk>/edit', SharedTransactionUpdate.as_view(), name="shared_transaction_update"),
    path('shared/transaction/<int:pk>/delete', SharedTransactionDelete.as_view(), name="shared_transaction_delete"),
    # mine
    path('mine', KakeiboTop.as_view(), name="kakeibo_top"),
    path('mine/list', KakeiboList.as_view(), name="kakeibo_list"),
    path('mine/<int:pk>', KakeiboDetail.as_view(), name="kakeibo_detail"),
    path('mine/<int:pk>/edit', KakeiboUpdate.as_view(), name="kakeibo_update"),
    path('mine/<int:pk>/delete', KakeiboDelete.as_view(), name="kakeibo_delete"),
    path('mine/create', KakeiboCreate.as_view(), name="kakeibo_create"),
    # path('mine/create_usd', KakeiboCreateUSD.as_view(), name="kakeibo_create_usd"),
    # Exchange
    path('exchange/create', ExchangeCreate.as_view(), name="exchange_create"),
    # event
    path('event/list', EventList.as_view(), name="event_list"),
    path('event/<int:pk>', EventDetail.as_view(), name="event_detail"),
    path('event/<int:pk>/edit', EventUpdate.as_view(), name="event_update"),
    path('event/<int:pk>/delete', EventDelete.as_view(), name="event_delete"),
    path('event/create', EventCreate.as_view(), name="event_create"),
    # autcomplete
    path('autocomplete/usage', UsageAutocomplete.as_view(), name="autocomplete_usage"),
    path('autocomplete/resource', ResourceAutocomplete.as_view(), name="autocomplete_resource"),
    # credit
    path('credit/import', CreditImport.as_view(), name="credit_import"),
    path('credit/link', CreditLink.as_view(), name="credit_link"),
    path('credit/link_from_kakeibo', CreditLinkFromKakeibo.as_view(), name="credit_link_from_kakeibo"),
    # other
    path('', RedirectView.as_view(url=reverse_lazy('kakeibo:kakeibo_top')))
]
