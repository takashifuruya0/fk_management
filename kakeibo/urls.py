# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from kakeibo.views import KakeiboTop

app_name = 'kakeibo'
urlpatterns = [
    path('', KakeiboTop.as_view(), name="top")
]