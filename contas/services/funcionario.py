from django.contrib.auth import get_user_model
from django.db import transaction
from contas.exceptions import (
    CampoImutavelErro,
    CampoObrigatorioErro,
    CPFCadastradoErro,
    EmailCadastradoErro,
    PermissaoNegadaErro,
)
from contas.models import (
    CargoFuncionario,
    HistoricoAuditoria,
    StatusAcesso,
    TipoOperacaoAuditoria,
    TipoPerfil,
)
from .validadores import (
    validar_cpf,
    validar_email,
    validar_nome,
    validar_senha,
    validar_telefone,
)

Usuario = get_user_model()


class FuncionarioService:
    @staticmethod
    @transaction.atomic
    def cadastrar(
        *,
        nome_completo: str,
        cpf: str,
        matricula_funcional: str,
        cargo: str,
        email: str,
        telefone: str,
        senha: str,
        confirmacao_senha: str,
        operador=None,
    ):
        cpf_valido = validar_cpf(cpf)
        nome_valido = validar_nome(nome_completo)
        email_valido = validar_email(email)
        telefone_valido = validar_telefone(telefone)
        validar_senha(senha, confirmacao_senha)

        matricula_limpa = (matricula_funcional or "").strip()
        if not matricula_limpa:
            raise CampoObrigatorioErro("Campo(s) obrigatório(s) não preenchido(s)")
        if len(matricula_limpa) > 20:
            matricula_limpa = matricula_limpa[:20]

        cargo_limpo = (cargo or "").strip()
        if not cargo_limpo:
            raise CampoObrigatorioErro("Campo(s) obrigatório(s) não preenchido(s)")

        if Usuario.objects.filter(cpf=cpf_valido).exists():
            raise CPFCadastradoErro("CPF já cadastrado")

        if Usuario.objects.filter(matricula_funcional=matricula_limpa).exists():
            raise CampoObrigatorioErro("Matrícula funcional já cadastrada")

        if Usuario.objects.filter(email__iexact=email_valido).exists():
            raise EmailCadastradoErro("E-mail já cadastrado")

        username = f"func_{matricula_limpa}"
        usuario = Usuario(
            username=username,
            nome_completo=nome_valido,
            cpf=cpf_valido,
            matricula_funcional=matricula_limpa,
            cargo=cargo_limpo[:60],
            email=email_valido,
            telefone=telefone_valido,
            tipo_perfil=TipoPerfil.FUNCIONARIO,
            status_acesso=StatusAcesso.ATIVO,
            is_staff=True,
        )
        usuario.set_password(senha)
        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=matricula_limpa,
            operador=operador or usuario,
            identificador_operador=getattr(operador, "matricula_funcional", None) or getattr(operador, "cpf", None) or (operador.username if operador else matricula_limpa),
            cargo_operador=getattr(operador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.CADASTRO_FUNCIONARIO,
            detalhes={"cargo": cargo_limpo, "matricula": matricula_limpa},
        )
        return usuario

    @staticmethod
    @transaction.atomic
    def editar_perfil(
        *,
        usuario,
        operador,
        nome_completo: str | None = None,
        cpf: str | None = None,
        matricula_funcional: str | None = None,
        cargo: str | None = None,
        email: str | None = None,
        telefone: str | None = None,
        nova_senha: str | None = None,
        confirmacao_nova_senha: str | None = None,
    ):
        if cpf is not None and usuario.cpf and cpf != usuario.cpf:
            raise CampoImutavelErro("O CPF e a Matrícula Funcional são os únicos campos que, após cadastrados, não poderão ser modificados.")

        if matricula_funcional is not None and usuario.matricula_funcional and matricula_funcional != usuario.matricula_funcional:
            raise CampoImutavelErro("O CPF e a Matrícula Funcional são os únicos campos que, após cadastrados, não poderão ser modificados.")

        modificacoes = {}

        if cargo is not None and cargo != usuario.cargo:
            if not getattr(operador, "is_administrador", False):
                raise PermissaoNegadaErro("O campo Cargo só poderá ser alterado por um usuário autenticado com nível de Administrador.")
            modificacoes["cargo"] = (usuario.cargo, cargo)
            usuario.cargo = cargo[:60]

        if nome_completo is not None:
            nome_valido = validar_nome(nome_completo)
            if nome_valido != usuario.nome_completo:
                modificacoes["nome_completo"] = (usuario.nome_completo, nome_valido)
                usuario.nome_completo = nome_valido

        if email is not None:
            email_valido = validar_email(email)
            if email_valido != usuario.email:
                if Usuario.objects.filter(email__iexact=email_valido).exclude(pk=usuario.pk).exists():
                    raise EmailCadastradoErro("E-mail já cadastrado")
                modificacoes["email"] = (usuario.email, email_valido)
                usuario.email = email_valido

        if telefone is not None:
            tel_valido = validar_telefone(telefone)
            if tel_valido != usuario.telefone:
                modificacoes["telefone"] = (usuario.telefone, tel_valido)
                usuario.telefone = tel_valido

        if nova_senha:
            validar_senha(nova_senha, confirmacao_nova_senha)
            usuario.set_password(nova_senha)
            modificacoes["senha"] = "Senha alterada"

        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=usuario.matricula_funcional or usuario.cpf or usuario.username,
            operador=operador,
            identificador_operador=getattr(operador, "matricula_funcional", None) or getattr(operador, "cpf", None) or operador.username,
            cargo_operador=getattr(operador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.ALTERACAO_CADASTRO,
            detalhes={"campos_alterados": list(modificacoes.keys())},
        )
        return usuario

    @staticmethod
    @transaction.atomic
    def inativar(usuario, operador):
        if not getattr(operador, "is_administrador", False):
            raise PermissaoNegadaErro("A exclusão lógica de funcionário somente poderá ser realizada por funcionários do cargo de Administradores.")

        usuario.status_acesso = StatusAcesso.INATIVO
        usuario.is_active = False
        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=usuario.matricula_funcional or usuario.cpf or usuario.username,
            operador=operador,
            identificador_operador=getattr(operador, "matricula_funcional", None) or getattr(operador, "cpf", None) or operador.username,
            cargo_operador=getattr(operador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.INATIVACAO_FUNCIONARIO,
            detalhes={"acao": "Inativação de acesso ao painel de ocorrências (exclusão lógica)"},
        )
        return usuario
