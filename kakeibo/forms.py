# coding: UTF-8
from django import forms
from django.contrib.auth import get_user_model
from kakeibo.models import Kakeibo, Usage, SharedKakeibo, Event, Resource, Exchange
from dal import autocomplete
from django.conf import settings


class KakeiboForm(forms.ModelForm):
    is_shared = forms.BooleanField(label="共通へコピー", required=False)
    event = forms.ModelChoiceField(
        label="イベント", queryset=Event.objects.filter(is_active=True, is_closed=False).order_by('-date'),
        required=False, widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Kakeibo
        fields = (
            "date", "fee", "currency",
            "way", 'usage', "resource_from", "resource_to", "memo",
            "event", "is_shared"
        )
        widgets = {
            "currency": forms.Select(attrs={"class": "form-control"}),
            'usage': autocomplete.ModelSelect2(url='kakeibo:autocomplete_usage'),
            "way": forms.Select(attrs={"class": "form-control"}),
            'resource_from': autocomplete.ModelSelect2(url='kakeibo:autocomplete_resource'),
            'resource_to': autocomplete.ModelSelect2(url='kakeibo:autocomplete_resource'),
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
        }


class KakeiboSearchForm(forms.Form):
    date_from = forms.DateField(
        label="開始日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"})
    )
    date_to = forms.DateField(
        label="終了日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"})
    )
    ways = forms.MultipleChoiceField(
        label="種別", required=False, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True),
        label="用途", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_usage')
    )
    resources_from = forms.ModelMultipleChoiceField(
        queryset=Resource.objects.filter(is_active=True),
        label="From", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_resource')
    )
    resources_to = forms.ModelMultipleChoiceField(
        queryset=Resource.objects.filter(is_active=True),
        label="To", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_resource')
    )
    memo = forms.CharField(label="メモ", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    currency = forms.ChoiceField(label="通貨", required=False, widget=forms.Select(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        self.base_fields['ways'].choices = settings.CHOICES_WAY
        self.base_fields['currency'].choices = settings.CHOICES_CURRENCY
        super().__init__(*args, **kwargs)


class SharedForm(forms.ModelForm):
    usage = forms.ModelChoiceField(
        queryset=Usage.objects.filter(is_active=True, is_shared=True).order_by('-name'),
        label="用途", required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = SharedKakeibo
        fields = ("date", "fee", "paid_by", 'usage', "memo")
        widgets = {
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "paid_by": forms.RadioSelect(),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
        }


class SharedSearchForm(forms.Form):
    date_from = forms.DateField(
        label="開始日", required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    date_to = forms.DateField(
        label="終了日", required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    paid_by = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(is_active=True),
        required=False, label="支払者", widget=forms.RadioSelect()
    )
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True, is_shared=True).order_by('-name'),
        label="用途", required=False, widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    memo = forms.CharField(label="メモ", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("date", "name", "memo", "detail", 'sum_plan', "is_closed")
        widgets = {
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "detail": forms.Textarea(attrs={"class": "form-control"}),
            "sum_plan": forms.NumberInput(attrs={"class": "form-control"}),
        }


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


class KakeiboUSDForm(forms.ModelForm):
    event = forms.ModelChoiceField(
        label="イベント", queryset=Event.objects.filter(is_active=True, is_closed=False).order_by('-date'),
        required=False, widget=forms.Select(attrs={"class": "form-control"})
    )
    currency = forms.CharField(label="Currency", required=True, initial="USD", disabled=True)

    class Meta:
        model = Kakeibo
        fields = (
            "date", "fee", "currency",
            "rate", "fee_converted",
            "way", 'usage', "resource_from", "resource_to", "memo",
            "event",
        )
        widgets = {
            'usage': autocomplete.ModelSelect2(url='kakeibo:autocomplete_usage'),
            "way": forms.Select(attrs={"class": "form-control"}),
            'resource_from': autocomplete.ModelSelect2(url='kakeibo:autocomplete_resource'),
            'resource_to': autocomplete.ModelSelect2(url='kakeibo:autocomplete_resource'),
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "rate": forms.NumberInput(attrs={"class": "form-control"}),
            "fee_converted": forms.NumberInput(attrs={"class": "form-control"}),
        }


class ExchangeForm(forms.ModelForm):
    fee_from = forms.IntegerField(label="Fee (From)", widget=forms.NumberInput(attrs={"class": "form-control"}))
    fee_to = forms.IntegerField(label="Fee (To)", widget=forms.NumberInput(attrs={"class": "form-control"}))
    resource_from = forms.ModelChoiceField(
        label="From", queryset=Resource.objects.filter(is_active=True, currency="JPY"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    resource_to = forms.ModelChoiceField(
        label="To", queryset=Resource.objects.filter(is_active=True, currency="USD"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Exchange
        fields = (
            "date", "method",
            "resource_from", "fee_from", "resource_to", "fee_to",
            "rate",  "commission", "currency"
        )
        widgets = {
            'date': forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "method": forms.Select(attrs={"class": "form-control"}),
            "currency": forms.Select(attrs={"class": "form-control"}),
            "rate": forms.NumberInput(attrs={"class": "form-control"}),
            "commission": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        exchange = super(ExchangeForm, self).save(commit=False)
        kf = Kakeibo.objects.create(
            date=self.cleaned_data['date'], fee=self.cleaned_data['fee_from'], way="振替",
            usage=Usage.objects.get(name="Exchange (From)"),
            resource_from=self.cleaned_data["resource_from"],
            currency=self.cleaned_data["resource_from"].currency
        )
        kt = Kakeibo.objects.create(
            date=self.cleaned_data['date'], fee=self.cleaned_data['fee_to'], way="振替",
            usage=Usage.objects.get(name="Exchange (To)"),
            resource_to=self.cleaned_data["resource_to"],
            currency=self.cleaned_data["resource_to"].currency
        )
        exchange.kakeibo_from = kf
        exchange.kakeibo_to = kt
        exchange.save()
        return exchange

# ==================================
# Mobile
# ==================================
# class MobileKakeiboForm(forms.ModelForm):
#     is_shared = forms.BooleanField(label="共通へコピー", required=False)
#     event = forms.ModelChoiceField(
#         label="イベント", queryset=Event.objects.filter(is_active=True, is_closed=False).order_by('-date'),
#         required=False, widget=forms.Select(attrs={"class": "form-control"})
#     )
#
#     class Meta:
#         model = Kakeibo
#         fields = (
#             "date", "fee", "currency",
#             "way", 'usage', "resource_from", "resource_to", "memo",
#             "event", "is_shared"
#         )
#         widgets = {
#             "currency": forms.Select(attrs={"class": "form-control"}),
#             'usage': forms.Select(attrs={"class": "form-control"}),
#             "way": forms.Select(attrs={"class": "form-control"}),
#             'resource_from': forms.Select(attrs={"class": "form-control"}),
#             'resource_to': forms.Select(attrs={"class": "form-control"}),
#             'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"}),
#             "memo": forms.TextInput(attrs={"class": "form-control"}),
#             "fee": forms.NumberInput(attrs={"class": "form-control"}),
#         }
#
#
# class MobileKakeiboSearchForm(forms.Form):
#     date_from = forms.DateField(
#         label="開始日", required=False,
#         widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"})
#     )
#     date_to = forms.DateField(
#         label="終了日", required=False,
#         widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"})
#     )
#     ways = forms.MultipleChoiceField(
#         label="種別", required=False, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
#     usages = forms.ModelMultipleChoiceField(
#         queryset=Usage.objects.filter(is_active=True),
#         label="用途", required=False,
#         widget=forms.Select(attrs={"class": "form-control"}),
#     )
#     resources_from = forms.ModelMultipleChoiceField(
#         queryset=Resource.objects.filter(is_active=True),
#         label="From", required=False,
#         widget=forms.Select(attrs={"class": "form-control"}),
#     )
#     resources_to = forms.ModelMultipleChoiceField(
#         queryset=Resource.objects.filter(is_active=True),
#         label="To", required=False,
#         widget=forms.Select(attrs={"class": "form-control"}),
#     )
#     memo = forms.CharField(label="メモ", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
#     currency = forms.ChoiceField(label="通貨", required=False, widget=forms.Select(attrs={"class": "form-control"}))
#
#     def __init__(self, *args, **kwargs):
#         self.base_fields['ways'].choices = settings.CHOICES_WAY
#         self.base_fields['currency'].choices = settings.CHOICES_CURRENCY
#         super().__init__(*args, **kwargs)


class MobileSharedForm(forms.ModelForm):
    usage = forms.ModelChoiceField(
        queryset=Usage.objects.filter(is_active=True, is_shared=True), label="用途",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    date2 = forms.DateField(
        label="日付", required=True,
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}))

    class Meta:
        model = SharedKakeibo
        fields = ("date2", "fee", "paid_by", 'usage', "memo")
        widgets = {
            'usage': forms.Select(attrs={"class": "form-control"}),
            "paid_by": forms.RadioSelect(),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        sk = super(MobileSharedForm, self).save(commit=False)
        sk.date = self.cleaned_data['date2']
        sk.save()
        return sk


class MobileSharedSearchForm(SharedSearchForm):
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True, is_shared=True),
        label="用途", required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    date_from = forms.DateField(
        label="開始日", required=False,
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"})
    )
    date_to = forms.DateField(
        label="終了日", required=False,
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"})
    )
