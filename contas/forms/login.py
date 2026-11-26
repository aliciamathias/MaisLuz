from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="CPF ou E-mail",
        widget=forms.TextInput(
            attrs={
                "class": "campo-input",
                "placeholder": "Digite seu CPF ou E-mail",
                "autocomplete": "username",
                "required": True,
            }
        ),
        error_messages={
            "required": "Campo(s) obrigatório(s) não preenchido(s)",
        },
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "campo-input",
                "placeholder": "Digite sua senha de acesso",
                "autocomplete": "current-password",
                "required": True,
            }
        ),
        error_messages={
            "required": "Campo(s) obrigatório(s) não preenchido(s)",
        },
    )

    error_messages = {
        "invalid_login": "Usuário ou senha inválidos",
        "inactive": "Usuário ou senha inválidos",
    }
