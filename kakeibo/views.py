from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from dal import autocomplete
from kakeibo.models import Kakeibo, Usage, Resource, Way
from kakeibo.forms import KakeiboForm, KakeiboSearchForm
# Create your views here.


class MyUserPasssesTestMixin(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.warning(self.request, "アクセス権限がありません")
        return redirect("top")


class KakeiboTop(MyUserPasssesTestMixin, TemplateView):
    template_name = "kakeibo_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resources"] = Resource.objects.filter(is_active=True).iterator()
        context["chart_header"] = list()
        context["chart_data"] = list()
        for r in Resource.objects.filter(is_active=True):
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
            print("usages: {}".format(self.request.GET.getlist('usages', None)))
            q = q.filter(usage__in=self.request.GET.getlist('usages'))
        # way
        if self.request.GET.getlist('ways', None):
            print("ways: {}".format(self.request.GET.getlist('ways', None)))
            q = q.filter(way__in=self.request.GET.getlist('ways'))
        return q.select_related('way', 'usage').order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        params = ""
        for k, vs in dict(self.request.GET).items():
            if not k == "page":
                for v in vs:
                    params = params + "&{}={}".format(k, v)
        context.update({
            'form': KakeiboForm(),
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
    # fields = ("date", "fee", "way", 'usage', "memo")

    def get_success_url(self):
        return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})


class KakeiboUpdate(MyUserPasssesTestMixin, UpdateView):
    template_name = "kakeibo_update.html"
    model = Kakeibo
    form_class = KakeiboForm

    def get_success_url(self):
        return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})


# =============================
# Autocomplete
# =============================
class UsageAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Usage.objects.none()
        qs = Usage.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class WayAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Way.objects.none()
        qs = Way.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
