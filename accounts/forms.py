from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from accounts.models import CustomUser


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', "first_name", "last_name")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("このユーザ名は登録済みです")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは登録済みです")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("パスワードが一致しません")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    # last_login = forms.DateTimeField(disabled=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'password',
            "username", "first_name", "last_name",
            'is_active', "is_staff", "is_superuser",
            "last_login", "date_joined",
        )

    def clean_password(self):
        return self.initial["password"]