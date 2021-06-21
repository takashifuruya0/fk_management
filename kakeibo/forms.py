from django import forms
from kakeibo.models import Kakeibo, Usage
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
        label="From",
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
    )
    date_to = forms.DateField(
        label="To",
        widget=forms.DateInput(attrs={'readonly': 'readonly', "class": "datepicker"})
    )