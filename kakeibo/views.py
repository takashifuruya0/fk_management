from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
# Create your views here.


class Top(TemplateView):
    template_name = "kakeibo_top.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
