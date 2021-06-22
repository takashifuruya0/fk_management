# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from kakeibo.views.views_kakeibo import KakeiboTop, KakeiboList, KakeiboDetail, KakeiboCreate, KakeiboUpdate
from kakeibo.views.views_autocomplete import UsageAutocomplete, WayAutocomplete, SharedUsageAutocomplete
from kakeibo.views.views_shared import SharedTop, SharedList, SharedDetail, SharedCreate, SharedUpdate

app_name = 'kakeibo'
urlpatterns = [
    # shared
    path('shared', SharedTop.as_view(), name="shared_top"),
    path('shared/list', SharedList.as_view(), name="shared_list"),
    path('shared/<int:pk>', SharedDetail.as_view(), name="shared_detail"),
    path('shared/<int:pk>/edit', SharedUpdate.as_view(), name="shared_update"),
    path('shared/create', SharedCreate.as_view(), name="shared_create"),
    # mine
    path('', KakeiboTop.as_view(), name="top"),
    path('kakeibo', KakeiboList.as_view(), name="kakeibo_list"),
    path('kakeibo/<int:pk>', KakeiboDetail.as_view(), name="kakeibo_detail"),
    path('kakeibo/<int:pk>/edit', KakeiboUpdate.as_view(), name="kakeibo_update"),
    path('kakeibo/create', KakeiboCreate.as_view(), name="kakeibo_create"),
    # autcomplete
    path('autocomplete/usage', UsageAutocomplete.as_view(), name="autocomplete_usage"),
    path('autocomplete/way', WayAutocomplete.as_view(), name="autocomplete_way"),
    path('autocomplete/shared/usage', SharedUsageAutocomplete.as_view(), name="autocomplete_shared_usage"),

]
