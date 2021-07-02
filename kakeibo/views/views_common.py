from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect


class MyUserPasssesTestMixin(UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.warning(self.request, "アクセス権限がありません")
        return redirect("top")