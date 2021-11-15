from django.db import models
from django.urls import reverse
from django.contrib import messages
from django.views.generic import TemplateView, CreateView
from datetime import date
from .views_common import MyUserPasssesTestMixin
from ..forms import IncomeForm, ExchangeForm, ExpenseForm, TransferForm, CreditImportForm
from ..models.models_kakeibo import Kakeibo, Exchange, Resource


class KakeiboTop(MyUserPasssesTestMixin, TemplateView):
    template_name = "v2/kakeibo_top.html"

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        initial_values = {
            "date": date.today(),
        }
        total = Kakeibo.objects.filter(is_active=True, resource_from=None) \
                    .exclude(resource_to=None) \
                    .aggregate(s=models.Sum('fee_converted'))['s'] \
                - Kakeibo.objects.filter(is_active=True, resource_to=None) \
                    .exclude(resource_from=None) \
                    .aggregate(s=models.Sum('fee_converted'))['s']
        data = {
            'income_form': IncomeForm(initial=initial_values),
            'expense_form': ExpenseForm(initial=initial_values),
            "exchange_form": ExchangeForm(initial=initial_values),
            "transfer_form": TransferForm(initial=initial_values),
            "credit_import_form": CreditImportForm(initial={"date_debit":date.today().strftime("%Y-%m")}),
            "total": total,
            "kakeibos": Kakeibo.objects.all_active().order_by("-pk")[:5],
            "resources": Resource.objects.all_active()
        }
        res.update(data)
        return res


class KakeiboIncomeCreate(MyUserPasssesTestMixin, CreateView):
    form_class = IncomeForm
    model = Kakeibo

    def get_success_url(self) -> str:
        messages.success(self.request, 'Created Income Kakeibo-{}'.format(self.object.pk))
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url


class KakeiboExpenseCreate(MyUserPasssesTestMixin, CreateView):
    form_class = ExpenseForm
    model = Kakeibo

    def get_success_url(self) -> str:
        messages.success(self.request, 'Created Expense Kakeibo-{}'.format(self.object.pk))
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url


class KakeiboExchangeCreate(MyUserPasssesTestMixin, CreateView):
    form_class = ExchangeForm
    model = Exchange

    def get_success_url(self) -> str:
        msg = 'Created Exchange-{} with Kakeibo-{} and Kakeibo-{}'.format(
            self.object.pk, self.object.kakeibo_from.pk, self.object.kakeibo_to.pk
            )
        messages.success(self.request, msg)
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url


class KakeiboTransferCreate(MyUserPasssesTestMixin, CreateView):
    form_class = TransferForm
    model = Kakeibo

    def get_success_url(self) -> str:
        msg = 'Created Transfer Kakeibo-{}'.format(self.object.pk)
        messages.success(self.request, msg)
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url

