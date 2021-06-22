from django import forms
from kakeibo.models import Kakeibo, Usage, Way
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
    usages = forms.ModelMultipleChoiceField(
        queryset=Usage.objects.filter(is_active=True),
        label="用途", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_usage')
    )
    ways = forms.ModelMultipleChoiceField(
        queryset=Way.objects.filter(is_active=True),
        label="種別", required=False,
        widget=autocomplete.ModelSelect2Multiple(url='kakeibo:autocomplete_way')
    )