from django import forms
from django.contrib.auth import get_user_model
from kakeibo.models import Kakeibo, Usage, Way, SharedKakeibo, Event
from dal import autocomplete
from django.conf import settings


class KakeiboForm(forms.ModelForm):
    is_shared = forms.BooleanField(label="共通へコピー")
    event = forms.ModelChoiceField(
        label="イベント", queryset=Event.objects.filter(is_active=True, is_closed=False).order_by('-date'),
        required=False, widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Kakeibo
        fields = ("date", "fee", "way", 'usage', "memo", "event", "is_shared")
        widgets = {
            'usage': autocomplete.ModelSelect2(url='kakeibo:autocomplete_usage', attrs={"class": "form-control"}),
            'way': autocomplete.ModelSelect2(url='kakeibo:autocomplete_way', attrs={"class": "form-control"}),
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"})
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
    types = forms.MultipleChoiceField(
        label="大分類", required=False,
        choices=(("支出", "支出"), ("収入", "収入"), ("振替", "振替"), ),
        widget=forms.CheckboxSelectMultiple()
    )
    ways = forms.ModelMultipleChoiceField(
        queryset=Way.objects.filter(is_active=True),
        label="種別", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_way', attrs={"class": "form-control"})
    )
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True),
        label="用途", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_usage', attrs={"class": "form-control"})
    )
    memo = forms.CharField(label="メモ", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))


class SharedForm(forms.ModelForm):
    class Meta:
        model = SharedKakeibo
        fields = ("date", "fee", "paid_by", 'usage', "memo")
        widgets = {
            'usage': autocomplete.ModelSelect2(
                url='kakeibo:autocomplete_shared_usage', attrs={"class": "form-control"}
            ),
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"}),
            "paid_by": forms.RadioSelect(),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
        }


class SharedSearchForm(forms.Form):
    date_from = forms.DateField(
        label="開始日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"})
    )
    date_to = forms.DateField(
        label="終了日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"})
    )
    paid_by = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(is_active=True), required=False,
        label="支払者",
        widget=forms.RadioSelect()
    )
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True, is_shared=True),
        label="用途", required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url='kakeibo:autocomplete_shared_usage', attrs={"class": "form-control"}
        )
    )
    memo = forms.CharField(label="メモ", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("date", "name", "memo", 'sum_plan', "is_closed")
        widgets = {
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "memo": forms.TextInput(attrs={"class": "form-control"}),
            "sum_plan": forms.NumberInput(attrs={"class": "form-control"}),
        }


class CreditImportForm(forms.Form):
    file = forms.FileField(label="ファイル", required=True, widget=forms.FileInput(attrs={"class": "form-control"}))
    date_debit = forms.DateField(
        label="請求年月", required=True,
        widget=forms.DateInput(attrs={"type": "month", "class": "form-control"})
    )
    card = forms.ChoiceField(label="カード", required=True, widget=forms.Select(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        self.base_fields['card'].choices = settings.CHOICES_CARD
        print(settings.CHOICES_CARD)
        print(self.base_fields['card'].choices)
        super().__init__(*args, **kwargs)

