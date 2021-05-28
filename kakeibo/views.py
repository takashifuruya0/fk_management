from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


class Top(TemplateView):
    template_name = "kakeibo_top.html"
