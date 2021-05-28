# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from kakeibo.views import Top

app_name = 'kakeibo'
urlpatterns = [
    path('', Top.as_view(), name="top")
]