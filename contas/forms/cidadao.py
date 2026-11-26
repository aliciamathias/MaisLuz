import re
from django import forms
from contas.exceptions import (
    CEPCurtoErro,
    CEPLongoErro,
    CPFInvalidoErro,
    EmailInvalidoErro,
    NomeCurtoErro,
    SenhaCurtaErro,
    SenhaLongaErro,
    SenhasDiferentesErro,
    TelefoneInvalidoErro,
)
from contas.services.validadores import (
    validar_cep,
    validar_cpf,
    validar_email,
    validar_nome,
    validar_senha,
    validar_telefone,
)


class CadastroCidadaoForm(forms.Form):
    nome = forms.CharField(
        max_length=120,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    cpf = forms.CharField(
        max_length=14,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    email = forms.CharField(
        max_length=200,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    celular = forms.CharField(
        max_length=14,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    senha = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    confirmacao_senha = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    cep = forms.CharField(
        max_length=30,
        required=True,
        error_messages={
            "required": "Campo(s) obrigatório(s) não preenchido(s)",
            "max_length": "CEP muito longo",
        },
    )
    logradouro = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    bairro = forms.CharField(
        max_length=100,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    numero = forms.CharField(
        max_length=10,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    complemento = forms.CharField(max_length=100, required=False)

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")
        try:
            return validar_nome(nome)
        except NomeCurtoErro as e:
            raise forms.ValidationError(str(e))

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        try:
            return validar_cpf(cpf)
        except CPFInvalidoErro as e:
            raise forms.ValidationError(str(e))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            return validar_email(email)
        except EmailInvalidoErro as e:
            raise forms.ValidationError(str(e))

    def clean_celular(self):
        celular = self.cleaned_data.get("celular")
        try:
            return validar_telefone(celular)
        except TelefoneInvalidoErro as e:
            raise forms.ValidationError(str(e))

    def clean_cep(self):
        cep = self.cleaned_data.get("cep")
        try:
            return validar_cep(cep)
        except (CEPCurtoErro, CEPLongoErro) as e:
            raise forms.ValidationError(str(e))

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmacao = cleaned_data.get("confirmacao_senha")

        if senha:
            try:
                validar_senha(senha, confirmacao)
            except (SenhaCurtaErro, SenhaLongaErro) as e:
                self.add_error("senha", str(e))
            except SenhasDiferentesErro as e:
                self.add_error("confirmacao_senha", str(e))

        return cleaned_data


class EdicaoPerfilCidadaoForm(forms.Form):
    nome = forms.CharField(
        max_length=120,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    email = forms.CharField(
        max_length=200,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    celular = forms.CharField(
        max_length=14,
        required=True,
        error_messages={"required": "Campo(s) obrigatório(s) não preenchido(s)"},
    )
    cep = forms.CharField(
        max_length=30,
        required=False,
        error_messages={"max_length": "CEP muito longo"},
    )
    logradouro = forms.CharField(
        max_length=100,
        required=False,
    )
    bairro = forms.CharField(
        max_length=100,
        required=False,
    )
    numero = forms.CharField(
        max_length=10,
        required=False,
    )
    complemento = forms.CharField(max_length=100, required=False)
    nova_senha = forms.CharField(max_length=100, required=False)
    confirmacao_nova_senha = forms.CharField(max_length=100, required=False)

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")
        try:
            return validar_nome(nome)
        except NomeCurtoErro as e:
            raise forms.ValidationError(str(e))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            return validar_email(email)
        except EmailInvalidoErro as e:
            raise forms.ValidationError(str(e))

    def clean_celular(self):
        celular = self.cleaned_data.get("celular")
        try:
            return validar_telefone(celular)
        except TelefoneInvalidoErro as e:
            raise forms.ValidationError(str(e))

    def clean_cep(self):
        cep = self.cleaned_data.get("cep")
        if cep:
            try:
                return validar_cep(cep)
            except (CEPCurtoErro, CEPLongoErro) as e:
                raise forms.ValidationError(str(e))
        return cep

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get("nova_senha")
        confirmacao = cleaned_data.get("confirmacao_nova_senha")

        if nova_senha:
            try:
                validar_senha(nova_senha, confirmacao)
            except (SenhaCurtaErro, SenhaLongaErro) as e:
                self.add_error("nova_senha", str(e))
            except SenhasDiferentesErro as e:
                self.add_error("confirmacao_nova_senha", str(e))

        return cleaned_data
