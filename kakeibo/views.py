from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, reverse
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
        return super().get_context_data(**kwargs)
