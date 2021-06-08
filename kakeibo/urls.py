# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from kakeibo.views import KakeiboTop, KakeiboList, KakeiboDetail, KakeiboCreate, KakeiboUpdate

app_name = 'kakeibo'
urlpatterns = [
    path('', KakeiboTop.as_view(), name="top"),
    path('kakeibo', KakeiboList.as_view(), name="kakeibo_list"),
    path('kakeibo/<int:pk>', KakeiboDetail.as_view(), name="kakeibo_detail"),
    path('kakeibo/<int:pk>/edit', KakeiboUpdate.as_view(), name="kakeibo_update"),
    path('kakeibo/create', KakeiboCreate.as_view(), name="kakeibo_create"),
]
