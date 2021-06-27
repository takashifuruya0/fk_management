from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.contrib import messages
import math
from kakeibo.models import SharedKakeibo, Budget, Usage
from kakeibo.forms import SharedForm, SharedSearchForm
# Create your views here.


class SharedTop(LoginRequiredMixin, TemplateView):
    template_name = "shared_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # year, month
        if self.request.GET.get("target_ym", None):
            target_ym = datetime.strptime(self.request.GET["target_ym"], "%Y-%m").date()
            last_ym = None
        else:
            target_ym = date.today()
        records_this_month = SharedKakeibo.objects.filter(
            is_active=True, date__year=target_ym.year, date__month=target_ym.month
        )
        # last month
        last_ym = target_ym - relativedelta(months=1)
        records_last_month = SharedKakeibo.objects.filter(
            is_active=True, date__year=last_ym.year, date__month=last_ym.month
        )
        # budget
        budget = Budget.objects.filter(date__lte=target_ym).latest('date')
        if records_this_month.exists():
            # Payment
            payment_total = records_this_month.aggregate(sum=Sum('fee'))['sum']
            payment_hoko = records_this_month.filter(paid_by__last_name="朋子").aggregate(sum=Sum('fee'))['sum']
            payment_takashi = payment_total - payment_hoko
            # Payment (%)
            pp_takashi = math.floor(100 * payment_takashi / payment_total)
            pp_hoko = 100 - pp_takashi
        else:
            # Payment
            payment_total = payment_hoko = payment_takashi = 0
            # Payment (%)
            pp_takashi = pp_hoko = 0
        # Black/Red
        diff = payment_total - budget.total
        is_black = diff < 0
        if is_black:
            # seisan
            seisan_hoko = budget.hoko + diff - payment_hoko
            seisan_takashi = 0 if seisan_hoko > 0 else abs(seisan_hoko)
            # budget (%)
            p_takashi = math.floor(100 * budget.takashi / budget.total)
            p_hoko = 100 - p_takashi
            p_over = 0
        else:
            # seisan
            seisan_hoko = budget.hoko + diff/2 - payment_hoko
            seisan_takashi = 0 if seisan_hoko > 0 else abs(seisan_hoko)
            # budget (%)
            p_over = math.floor(100 * abs(diff) / (budget.total + diff))
            p_takashi = math.floor(100 * budget.takashi / (budget.total + diff))
            p_hoko = 100 - p_takashi - p_over
        seisan_hoko = 0 if seisan_hoko < 0 else math.floor(seisan_hoko/1000)*1000
        # usage
        group_by_usage_tm = records_this_month.values('usage__name').annotate(sum=Sum('fee')).order_by('-sum')
        group_by_usage_lm = records_last_month.values('usage__name').annotate(sum=Sum('fee')).order_by('-sum')
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
            "target_ym": target_ym,
            "payment": {
                "takashi": payment_takashi,
                "hoko": payment_hoko,
                "total": payment_total,
            },
            "p_payment": {
                "takashi": pp_takashi,
                "hoko": pp_hoko,
            },
            "seisan": {
                "takashi": seisan_takashi,
                "hoko": seisan_hoko,
            },
            "group_by_usage": {
                "tm": group_by_usage_tm,
                "lm": group_by_usage_lm,
            }
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
            q = q.filter(usage__in=self.request.GET.getlist('usages'))
        # memo
        if self.request.GET.get("memo", None):
            q = q.filter(memo__icontains=self.request.GET("memo"))
        return q.select_related('paid_by', 'usage').order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        params = ""
        for k, vs in dict(self.request.GET).items():
            if not k == "page":
                for v in vs:
                    params = params + "&{}={}".format(k, v)
        if params:
            messages.info(self.request, "検索結果を表示します。{}".format(params))
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

