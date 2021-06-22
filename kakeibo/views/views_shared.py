from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.db.models import Q
from kakeibo.models import Kakeibo, Usage, Resource, Way, SharedKakeibo
from kakeibo.forms import SharedForm, SharedSearchForm
# Create your views here.


class SharedTop(LoginRequiredMixin, TemplateView):
    template_name = "shared_top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resources"] = Resource.objects.filter(is_active=True).iterator()
        context["chart_header"] = list()
        context["chart_data"] = list()
        for r in Resource.objects.filter(is_active=True):
            context["chart_header"].append(r.name)
            context["chart_data"].append(r.total)
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

