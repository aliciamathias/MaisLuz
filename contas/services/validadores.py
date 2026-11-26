import re
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

PADRAO_CPF = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
PADRAO_TELEFONE = re.compile(r"^\(\d{2}\)9\d{4}-\d{4}$")
PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_cpf(cpf: str) -> str:
    if not cpf or not PADRAO_CPF.match(cpf.strip()):
        raise CPFInvalidoErro("CPF não identificado")
    return cpf.strip()


def validar_nome(nome: str) -> str:
    nome_limpo = (nome or "").strip()
    if len(nome_limpo) < 3:
        raise NomeCurtoErro("Nome muito curto")
    if len(nome_limpo) > 120:
        return nome_limpo[:120]
    return nome_limpo


def validar_telefone(telefone: str) -> str:
    tel_limpo = (telefone or "").strip()
    if len(tel_limpo) != 14 or not PADRAO_TELEFONE.match(tel_limpo):
        raise TelefoneInvalidoErro("Telefone inválido")
    return tel_limpo


def validar_email(email: str) -> str:
    email_limpo = (email or "").strip()
    if not email_limpo or len(email_limpo) > 200 or not PADRAO_EMAIL.match(email_limpo):
        raise EmailInvalidoErro("Email inválido")
    return email_limpo


def validar_senha(senha: str, confirmacao_senha: str | None = None) -> str:
    if len(senha) < 8:
        raise SenhaCurtaErro("A senha é muito curta")
    if len(senha) > 30:
        raise SenhaLongaErro("A senha é muito longa")
    if confirmacao_senha is not None and senha != confirmacao_senha:
        raise SenhasDiferentesErro("As senhas são diferentes")
    return senha


def validar_cep(cep: str) -> str:
    cep_digitos = re.sub(r"\D", "", cep or "")
    if len(cep_digitos) < 8:
        raise CEPCurtoErro("CEP muito curto")
    if len(cep_digitos) > 8:
        raise CEPLongoErro("CEP muito longo")
    return cep_digitos
