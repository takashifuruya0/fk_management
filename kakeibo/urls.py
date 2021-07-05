# coding:utf-8
from django.urls import path
from kakeibo.views.views_kakeibo import KakeiboTop, KakeiboList, KakeiboDetail, KakeiboCreate, KakeiboUpdate
from kakeibo.views.views_kakeibo import EventList, EventCreate, EventUpdate, EventDetail
from kakeibo.views.views_kakeibo import KakeiboCreateUSD
from kakeibo.views.views_autocomplete import UsageAutocomplete, SharedUsageAutocomplete, ResourceAutocomplete
from kakeibo.views.views_shared import SharedTop, SharedList, SharedDetail, SharedCreate, SharedUpdate
from kakeibo.views.views_shared import MobileSharedCreate, MobileSharedUpdate
from kakeibo.views.views_credit import CreditImport, CreditLink, CreditLinkFromKakeibo

app_name = 'kakeibo'
urlpatterns = [
    # shared
    path('shared', SharedTop.as_view(), name="shared_top"),
    path('shared/list', SharedList.as_view(), name="shared_list"),
    path('shared/<int:pk>', SharedDetail.as_view(), name="shared_detail"),
    path('shared/<int:pk>/edit', SharedUpdate.as_view(), name="shared_update"),
    path('shared/create', SharedCreate.as_view(), name="shared_create"),
    path('shared/<int:pk>/edit_mobile', MobileSharedUpdate.as_view(), name="shared_update_mobile"),
    path('shared/create_mobile', MobileSharedCreate.as_view(), name="shared_create_mobile"),
    # mine
    path('mine', KakeiboTop.as_view(), name="kakeibo_top"),
    path('mine/list', KakeiboList.as_view(), name="kakeibo_list"),
    path('mine/<int:pk>', KakeiboDetail.as_view(), name="kakeibo_detail"),
    path('mine/<int:pk>/edit', KakeiboUpdate.as_view(), name="kakeibo_update"),
    path('mine/create', KakeiboCreate.as_view(), name="kakeibo_create"),
    path('mine/create_usd', KakeiboCreateUSD.as_view(), name="kakeibo_create_usd"),
    # event
    path('event/list', EventList.as_view(), name="event_list"),
    path('event/<int:pk>', EventDetail.as_view(), name="event_detail"),
    path('event/<int:pk>/edit', EventUpdate.as_view(), name="event_update"),
    path('event/create', EventCreate.as_view(), name="event_create"),
    # autcomplete
    path('autocomplete/usage', UsageAutocomplete.as_view(), name="autocomplete_usage"),
    path('autocomplete/resource', ResourceAutocomplete.as_view(), name="autocomplete_resource"),
    path('autocomplete/shared/usage', SharedUsageAutocomplete.as_view(), name="autocomplete_shared_usage"),
    # credit
    path('credit/import', CreditImport.as_view(), name="credit_import"),
    path('credit/link', CreditLink.as_view(), name="credit_link"),
    path('credit/link_from_kakeibo', CreditLinkFromKakeibo.as_view(), name="credit_link_from_kakeibo")

]
