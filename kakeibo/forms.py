from django import forms
from django.contrib.auth import get_user_model
from kakeibo.models import Kakeibo, Usage, Way, SharedKakeibo
from dal import autocomplete


class KakeiboForm(forms.ModelForm):
    class Meta:
        model = Kakeibo
        fields = ("date", "fee", "way", 'usage', "memo")
        widgets = {
            'usage': autocomplete.ModelSelect2(url='kakeibo:autocomplete_usage'),
            'way': autocomplete.ModelSelect2(url='kakeibo:autocomplete_way'),
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
        }


class KakeiboSearchForm(forms.Form):
    date_from = forms.DateField(
        label="開始日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
    )
    date_to = forms.DateField(
        label="終了日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
    )
    types = forms.MultipleChoiceField(
        label="大分類", required=False,
        choices=(("支出", "支出"), ("収入", "収入"), ("振替", "振替"), ),
        widget=forms.CheckboxSelectMultiple()
    )
    ways = forms.ModelMultipleChoiceField(
        queryset=Way.objects.filter(is_active=True),
        label="種別", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_way')
    )
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True),
        label="用途", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_usage')
    )
    memo = forms.CharField(label="メモ", required=False)


class SharedForm(forms.ModelForm):
    class Meta:
        model = SharedKakeibo
        fields = ("date", "fee", "paid_by", 'usage', "memo")
        widgets = {
            'usage': autocomplete.ModelSelect2(url='kakeibo:autocomplete_shared_usage'),
            'date': forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"}),
            "paid_by": forms.RadioSelect(),
        }


class SharedSearchForm(forms.Form):
    date_from = forms.DateField(
        label="開始日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
    )
    date_to = forms.DateField(
        label="終了日", required=False,
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
    )
    paid_by = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.filter(is_active=True), required=False,
        label="支払者",
        widget=forms.RadioSelect()
    )
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True, is_shared=True),
        label="用途", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_shared_usage')
    )
    memo = forms.CharField(label="メモ", required=False)