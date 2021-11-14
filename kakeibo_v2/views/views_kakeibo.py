from django.db import models
from django.urls import reverse
from django.contrib import messages
from django.views.generic import TemplateView, CreateView
from datetime import date
from ..forms import IncomeForm, ExchangeForm, ExpenseForm, TransferForm
from ..models import Kakeibo, Exchange


class KakeiboTop(TemplateView):
    template_name = "v2/kakeibo_top.html"

    def get_context_data(self, **kwargs):
        initial_values = {
            "date": date.today(),
        }
        res = super().get_context_data(**kwargs)
        data = {
            'income_form': IncomeForm(initial=initial_values),
            'expense_form': ExpenseForm(initial=initial_values),
            "exchange_form": ExchangeForm(initial=initial_values),
            "transfer_form": TransferForm(initial=initial_values)
        }
        res.update(data)
        return res


class KakeiboIncomeCreate(CreateView):
    form_class = IncomeForm
    model = Kakeibo

    def get_success_url(self) -> str:
        messages.success(self.request, 'Created Income Kakeibo-{}'.format(self.object.pk))
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url


class KakeiboExpenseCreate(CreateView):
    form_class = ExpenseForm
    model = Kakeibo

    def get_success_url(self) -> str:
        messages.success(self.request, 'Created Expense Kakeibo-{}'.format(self.object.pk))
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url


class KakeiboExchangeCreate(CreateView):
    form_class = ExchangeForm
    model = Exchange

    def get_success_url(self) -> str:
        msg = 'Created Exchange-{} with Kakeibo-{} and Kakeibo-{}'.format(
            self.object.pk, self.object.kakeibo_from.pk, self.object.kakeibo_to.pk
            )
        messages.success(self.request, msg)
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url


class KakeiboTransferCreate(CreateView):
    form_class = TransferForm
    model = Kakeibo

    def get_success_url(self) -> str:
        msg = 'Created Transfer Kakeibo-{}'.format(self.object.pk)
        messages.success(self.request, msg)
        success_url = reverse("kakeibo_v2:kakeibo_top")
        return success_url

