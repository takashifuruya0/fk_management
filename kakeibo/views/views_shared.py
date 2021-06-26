from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from datetime import date
from django.db.models import Sum
import math
from kakeibo.models import SharedKakeibo, Budget, Usage
from kakeibo.forms import SharedForm, SharedSearchForm
# Create your views here.


class SharedTop(LoginRequiredMixin, TemplateView):
    template_name = "shared_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        records_this_month = SharedKakeibo.objects.filter(is_active=True, date__year=today.year, date__month=today.month)
        # budget
        budget = Budget.objects.latest('date')
        # Black/Red
        # sum_this_month = records_this_month.aggregate(sum=Sum('fee'))['sum']
        payment_total = 171000
        payment_hoko = 36000
        payment_takashi = 135000
        pp_takashi = math.floor(100 * payment_takashi / payment_total)
        pp_hoko = 100 - pp_takashi
        diff = payment_total - budget.total
        is_black = diff < 0
        if is_black:
            seisan = budget.hoko + diff - payment_hoko
            # over
            p_takashi = math.floor(100 * budget.takashi / budget.total)
            p_hoko = 100 - p_takashi
            p_over = 0
        else:
            seisan = budget.hoko + diff/2 - payment_hoko
            # over
            p_over = math.floor(100 * abs(diff) / (budget.total + diff))
            p_takashi = math.floor(100 * budget.takashi / (budget.total + diff))
            p_hoko = 100 - p_takashi - p_over
        # return
        context.update({
            "budget": budget,
            'p_budget': {
                "takashi": p_takashi,
                "hoko": p_hoko,
                "over": p_over,
            },
            "diff": diff,
            "is_black": is_black,
            "today": today,
            "payment": {
                "takashi": payment_takashi,
                "hoko": payment_hoko,
                "total": payment_total,
            },
            "p_payment": {
                "takashi": pp_takashi,
                "hoko": pp_hoko,
            },
            "seisan": seisan,
        })
        return context


class SharedList(LoginRequiredMixin, ListView):
    template_name = "shared_list.html"
    model = SharedKakeibo
    paginate_by = 20

    def get_queryset(self):
        q = SharedKakeibo.objects.filter(is_active=True)
        # date
        if self.request.GET.get('date_from', None) and self.request.GET.get('date_to', None):
            q = q.filter(date__range=(self.request.GET['date_from'], self.request.GET['date_to']))
        elif self.request.GET.get('date_from', None):
            q = q.filter(date__gte=self.request.GET['date_from'])
        elif self.request.GET.get('date_to', None):
            q = q.filter(date__lte=self.request.GET['date_to'])
        # usage
        if self.request.GET.getlist('usages', None):
            print("usages: {}".format(self.request.GET.getlist('usages', None)))
            q = q.filter(usage__in=self.request.GET.getlist('usages'))
        return q.select_related('paid_by', 'usage').order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        params = ""
        for k, vs in dict(self.request.GET).items():
            if not k == "page":
                for v in vs:
                    params = params + "&{}={}".format(k, v)
        context.update({
            'form': SharedForm(),
            "search_form": SharedSearchForm(self.request.GET),
            "params": params
        })
        return context


class SharedDetail(LoginRequiredMixin, DetailView):
    template_name = "shared_detail.html"
    model = SharedKakeibo


class SharedCreate(LoginRequiredMixin, CreateView):
    template_name = "shared_create.html"
    model = SharedKakeibo
    form_class = SharedForm

    def get_success_url(self):
        return reverse("kakeibo:shared_detail", kwargs={"pk": self.object.pk})


class SharedUpdate(LoginRequiredMixin, UpdateView):
    template_name = "shared_update.html"
    model = SharedKakeibo
    form_class = SharedForm

    def get_success_url(self):
        return reverse("kakeibo:shared_detail", kwargs={"pk": self.object.pk})

