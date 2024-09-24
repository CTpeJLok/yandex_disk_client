from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    password_confirm = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data: dict = super().clean()
        password: str = str(cleaned_data.get("password"))
        password_confirm: str = str(cleaned_data.get("password_confirm"))

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Пароли не совпадают")

        try:
            validate_password(password)
        except ValidationError:
            self.add_error("password", "Пароль слишком легкий")

        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
