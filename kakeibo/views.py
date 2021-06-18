from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
from kakeibo.models import *
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
        context["resources"] = Resource.objects.filter(is_active=True)
        context["ways"] = Way.objects.filter(is_active=True)
        return context


class KakeiboList(MyUserPasssesTestMixin, ListView):
    template_name = "kakeibo_list.html"
    model = Kakeibo
    paginate_by = 20


class KakeiboDetail(MyUserPasssesTestMixin, DetailView):
    template_name = "kakeibo_detail.html"
    model = Kakeibo


class KakeiboCreate(MyUserPasssesTestMixin, CreateView):
    template_name = "kakeibo_create.html"
    model = Kakeibo
    fields = ("date", "fee", "way", 'usage', "memo")

    def get_success_url(self):
        return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form()
        form.fields['date'].widget.attrs['readonly'] = 'readonly'
        form.fields['date'].widget.attrs['class'] = 'datepicker'
        return form


class KakeiboUpdate(MyUserPasssesTestMixin, UpdateView):
    template_name = "kakeibo_update.html"
    model = Kakeibo
    fields = ("date", "fee", "way", 'usage', "memo")

    def get_success_url(self):
        return reverse("kakeibo:kakeibo_detail", kwargs={"pk": self.object.pk})