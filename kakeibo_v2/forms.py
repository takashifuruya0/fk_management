# coding: UTF-8
from django import forms
from django.contrib.auth import get_user_model
from dal import autocomplete
from django.conf import settings
from .models.models_kakeibo import Kakeibo, Usage, Event, Resource, Exchange
from .models.models_base import CHOICES_CURRENCY
from .functions import money



class IncomeForm(forms.ModelForm):
    """
    Form for Income
    """
    usage = forms.ModelChoiceField(
        label="収入種類", queryset=Usage.objects.filter(is_active=True, way="収入").order_by('name'),
        required=True, widget=forms.Select(attrs={"class": "form-control"})
    )
    resource_to = forms.ModelChoiceField(
        label="口座", queryset=Resource.objects.all_active(),
        required=True, widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Kakeibo
        fields = (
            "date", "fee", "currency",
            'usage', "resource_to", "memo",
        )
        widgets = {
            "currency": forms.Select(attrs={"class": "form-control"}),
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        data = {
            "way": "収入",
        }
        self.cleaned_data.update(data)
        k = Kakeibo.objects.create(**self.cleaned_data)
        return k



class ExpenseForm(forms.ModelForm):
    """
    Form for Expenses
    """
    usage = forms.ModelChoiceField(
        label="支出用途", queryset=Usage.objects.filter(is_active=True, way="支出").order_by('name'),
        required=True, widget=forms.Select(attrs={"class": "form-control"})
    )
    event = forms.ModelChoiceField(
        label="イベント", queryset=Event.objects.filter(is_active=True, is_closed=False).order_by('-date'),
        required=False, widget=forms.Select(attrs={"class": "form-control"})
    )
    is_shared = forms.BooleanField(label="共通へコピー", required=False)

    class Meta:
        model = Kakeibo
        fields = (
            "date", "fee", "currency",
            'usage', "resource_from", "card", 'rate', "memo",
            "event", "is_shared"
        )
        widgets = {
            "currency": forms.Select(attrs={"class": "form-control"}),
            'resource_from': forms.Select(attrs={"class": "form-control"}),
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "rate": forms.NumberInput(attrs={"class": "form-control"}),
        }
    
    def save(self, commit=True):
        data = {
            "way": "支出",
        }
        self.cleaned_data.update(data)
        k = Kakeibo.objects.create(**self.cleaned_data)
        return k



class CreditImportForm(forms.Form):
    file = forms.FileField(
        label="ファイル", required=True, widget=forms.FileInput(attrs={"class": "form-control"})
    )
    date_debit = forms.DateField(
        label="請求年月", required=True, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    card = forms.ChoiceField(label="カード", required=True, widget=forms.Select(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        self.base_fields['card'].choices = settings.CHOICES_CARD
        super().__init__(*args, **kwargs)



class ExchangeForm(forms.ModelForm):
    """
    Form for Exchanges
    """
    fee_from = forms.DecimalField(label="Fee (From)", widget=forms.NumberInput(attrs={"class": "form-control"}))
    fee_to = forms.DecimalField(label="Fee (To)", widget=forms.NumberInput(attrs={"class": "form-control"}))
    currency_from = forms.ChoiceField(
        label="Currency (From)", choices=CHOICES_CURRENCY, 
        widget=forms.Select(attrs={"class": "form-control"})
        )
    currency_to = forms.ChoiceField(
        label="Currency (To)", choices=CHOICES_CURRENCY, 
        widget=forms.Select(attrs={"class": "form-control"})
        )
    resource_from = forms.ModelChoiceField(
        label="From", queryset=Resource.objects.filter(is_active=True).order_by('-name'),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    resource_to = forms.ModelChoiceField(
        label="To", queryset=Resource.objects.filter(is_active=True).order_by('-name'),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Exchange
        fields = (
            "date", "method",
            "resource_from", "fee_from", "currency_from", 
            "resource_to", "fee_to", "currency_to",
            "rate", 
        )
        widgets = {
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "method": forms.Select(attrs={"class": "form-control"}),
            "rate": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        exchange = super(ExchangeForm, self).save(commit=False)
        rf = None if self.cleaned_data["currency_from"] == "JPY" else self.cleaned_data["rate"] 
        kf = Kakeibo.objects.create(
            date=self.cleaned_data['date'], fee=self.cleaned_data['fee_from'], way="両替",
            usage=Usage.objects.get(name="Exchange (From)"), rate=rf,
            resource_from=self.cleaned_data["resource_from"],
            currency=self.cleaned_data["currency_from"]
        )
        rt = None if self.cleaned_data["currency_to"] == "JPY" else self.cleaned_data["rate"] 
        kt = Kakeibo.objects.create(
            date=self.cleaned_data['date'], fee=self.cleaned_data['fee_to'], way="両替",
            usage=Usage.objects.get(name="Exchange (To)"), rate=rt,
            resource_to=self.cleaned_data["resource_to"],
            currency=self.cleaned_data["currency_to"]
        )
        exchange.kakeibo_from = kf
        exchange.kakeibo_to = kt
        exchange.save()
        return exchange


class TransferForm(forms.ModelForm):
    """
    Form for Transfer
    """

    class Meta:
        model = Kakeibo
        fields = (
            "date", "fee", "currency", "resource_from", 'resource_to', "memo",
        )
        widgets = {
            'resource_from': forms.Select(attrs={"class": "form-control"}),
            'resource_to': forms.Select(attrs={"class": "form-control"}),
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
        }
    
    def save(self, commit=True):
        data = {
            "way": "振替",
            "usage": Usage.objects.get(name="振替"),
        }
        self.cleaned_data.update(data)
        k = Kakeibo.objects.create(**self.cleaned_data)
        return k
    