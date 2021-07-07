from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib import messages
from django.shortcuts import reverse
from django.db import transaction
from django import forms
from kakeibo.views.views_common import MyUserPasssesTestMixin
from kakeibo.models import Kakeibo, Resource, SharedKakeibo, Event, Exchange
from kakeibo.forms import KakeiboForm, KakeiboSearchForm, EventForm, CreditImportForm, KakeiboUSDForm, ExchangeForm
from datetime import date
import logging
logger = logging.getLogger('django')
# Create your views here.


class KakeiboTop(MyUserPasssesTestMixin, TemplateView):
    template_name = "kakeibo_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resources = Resource.objects.prefetch_related('resource_from', "resource_to").filter(is_active=True)\
            .exclude(resource_from=None, resource_to=None).order_by('currency')
        context.update({
            "resources": resources.iterator(),
            "chart_header": list(),
            "chart_data": list(),
            "form": KakeiboForm(initial={"date": date.today()}),
            "credit_import_form": CreditImportForm(),
            "usd_form": KakeiboUSDForm(initial={"date": date.today()}),
            "exchange_form": ExchangeForm(initial={"date": date.today()}),
        })
        for r in resources:
            context["chart_header"].append(r.name)
            context["chart_data"].append(r.total)
        return context


class KakeiboList(MyUserPasssesTestMixin, ListView):
    template_name = "kakeibo_list.html"
    model = Kakeibo
    paginate_by = 20

    def get_queryset(self):
        q = Kakeibo.objects.filter(is_active=True)
        # date
        if self.request.GET.get('date_from', None) and self.request.GET.get('date_to', None):
            q = q.filter(date__range=(self.request.GET['date_from'], self.request.GET['date_to']))
        elif self.request.GET.get('date_from', None):
            q = q.filter(date__gte=self.request.GET['date_from'])
        elif self.request.GET.get('date_to', None):
            q = q.filter(date__lte=self.request.GET['date_to'])
        # usage
        if self.request.GET.getlist('usages', None):
            logger.info("usages: {}".format(self.request.GET.getlist('usages', None)))
            q = q.filter(usage__in=self.request.GET.getlist('usages'))
        # way
        if self.request.GET.getlist('ways', None):
            logger.info("ways: {}".format(self.request.GET.getlist('ways', None)))
            q = q.filter(way__in=self.request.GET.getlist('ways'))
        # resource_from
        if self.request.GET.getlist('resources_from', None):
            logger.info("resources_from: {}".format(self.request.GET.getlist('resources_from', None)))
            q = q.filter(resource_from__in=self.request.GET.getlist('resources_from'))
        # resource_to
        if self.request.GET.getlist('resources_to', None):
            logger.info("resources_to: {}".format(self.request.GET.getlist('resources_to', None)))
            q = q.filter(resource_to__in=self.request.GET.getlist('resources_to'))
        # memo
        if self.request.GET.get("memo", None):
            q = q.filter(memo__icontains=self.request.GET["memo"])
        # memo
        if self.request.GET.get("currency", None):
            q = q.filter(currency=self.request.GET["currency"])
        return q.select_related('usage', "resource_from", "resource_to").order_by('-date')

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
            'form': KakeiboForm(initial={"date": date.today(),}),
            "search_form": KakeiboSearchForm(self.request.GET),
            "params": params
        })
        return context


class KakeiboDetail(MyUserPasssesTestMixin, DetailView):
    template_name = "kakeibo_detail.html"
    model = Kakeibo


class KakeiboCreate(MyUserPasssesTestMixin, CreateView):
    template_name = "kakeibo_create.html"
    model = Kakeibo
    form_class = KakeiboForm

    def get_success_url(self):
        messages.success(self.request, "家計簿作成に成功しました")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        with transaction.atomic():
            res = super(KakeiboCreate, self).form_valid(form)
            kakeibo = self.object
            if form.cleaned_data['is_shared']:
                shared = SharedKakeibo(
                    date=kakeibo.date, fee=kakeibo.fee, usage=kakeibo.usage,
                    memo=kakeibo.memo, paid_by=self.request.user
                )
                shared.save()
                kakeibo.shared = shared
                kakeibo.save()
        return res

    def form_invalid(self, form):
        messages.error(self.request, "家計簿作成に失敗しました {}".format(form.errors))
        return super(KakeiboCreate, self).form_invalid(form)


class KakeiboUpdate(MyUserPasssesTestMixin, UpdateView):
    template_name = "kakeibo_update.html"
    model = Kakeibo

    def get_form_class(self):
        if self.object.currency == "USD":
            return KakeiboUSDForm
        else:
            return KakeiboForm

    def get_form(self, form_class=None):
        form = super().get_form()
        if form.fields.get("is_shared", None):
            form.fields['is_shared'].widget = forms.HiddenInput()
        return form

    def get_success_url(self):
        messages.success(self.request, "家計簿更新に成功しました")
        return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})


# =================================
# Event
# =================================
class EventList(MyUserPasssesTestMixin, ListView):
    template_name = "event_list.html"
    model = Event
    paginate_by = 20
    queryset = Event.objects.filter(is_active=True).order_by('-date', "is_closed")


class EventDetail(MyUserPasssesTestMixin, DetailView):
    template_name = "event_detail.html"
    model = Event


class EventCreate(MyUserPasssesTestMixin, CreateView):
    template_name = "event_create.html"
    model = Event
    form_class = EventForm

    def get_success_url(self):
        messages.success(self.request, "イベント作成に成功しました")
        return reverse("kakeibo:event_detail", kwargs={"pk": self.object.pk})


class EventUpdate(MyUserPasssesTestMixin, UpdateView):
    template_name = "event_update.html"
    model = Event
    form_class = EventForm

    def get_success_url(self):
        messages.success(self.request, "イベント更新に成功しました")
        return reverse("kakeibo:event_detail", kwargs={"pk": self.object.pk})


# =================================
# USD
# =================================
class KakeiboCreateUSD(MyUserPasssesTestMixin, CreateView):
    template_name = "kakeibo_create.html"
    model = Kakeibo
    form_class = KakeiboUSDForm

    def get_success_url(self):
        messages.success(self.request, "Successfully Created Kakeibo")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        return super(KakeiboCreateUSD, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create Kakeibo: {}".format(form.errors))
        return super(KakeiboCreateUSD, self).form_invalid(form)


class ExchangeCreate(CreateView):
    form_class = ExchangeForm
    model = Exchange

    def get_success_url(self):
        messages.success(self.request, "Successfully Created Exchange")
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse("kakeibo:kakeibo_top")