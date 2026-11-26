from django.contrib.auth import get_user_model
from django.db import transaction
from contas.exceptions import (
    CampoImutavelErro,
    CampoObrigatorioErro,
    CPFCadastradoErro,
    EmailCadastradoErro,
)
from contas.models import HistoricoAuditoria, StatusAcesso, TipoOperacaoAuditoria, TipoPerfil
from .validadores import (
    validar_cep,
    validar_cpf,
    validar_email,
    validar_nome,
    validar_senha,
    validar_telefone,
)

Usuario = get_user_model()


class CidadaoService:
    @staticmethod
    @transaction.atomic
    def cadastrar(
        *,
        nome_completo: str,
        cpf: str,
        email: str,
        telefone: str,
        senha: str,
        confirmacao_senha: str,
        cep: str,
        logradouro: str,
        bairro: str,
        numero: str,
        complemento: str = "",
    ):
        cpf_valido = validar_cpf(cpf)
        nome_valido = validar_nome(nome_completo)
        email_valido = validar_email(email)
        telefone_valido = validar_telefone(telefone)
        validar_senha(senha, confirmacao_senha)
        cep_valido = validar_cep(cep)

        if not logradouro or not bairro or not numero:
            raise CampoObrigatorioErro("Campo(s) obrigatório(s) não preenchido(s)")

        if Usuario.objects.filter(cpf=cpf_valido).exists():
            raise CPFCadastradoErro("CPF já cadastrado")

        if Usuario.objects.filter(email__iexact=email_valido).exists():
            raise EmailCadastradoErro("E-mail já cadastrado")

        username = f"cid_{cpf_valido.replace('.', '').replace('-', '')}"
        usuario = Usuario(
            username=username,
            nome_completo=nome_valido,
            cpf=cpf_valido,
            email=email_valido,
            telefone=telefone_valido,
            tipo_perfil=TipoPerfil.CIDADAO,
            status_acesso=StatusAcesso.ATIVO,
            cep=cep_valido,
            logradouro=logradouro[:100],
            bairro=bairro[:100],
            numero=numero[:10],
            complemento=(complemento or "")[:100],
        )
        usuario.set_password(senha)
        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=cpf_valido,
            operador=usuario,
            identificador_operador=cpf_valido,
            tipo_operacao=TipoOperacaoAuditoria.CADASTRO_CIDADAO,
            detalhes={"acao": "Cadastro de novo cidadão via formulário público"},
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
        email: str | None = None,
        telefone: str | None = None,
        cep: str | None = None,
        logradouro: str | None = None,
        bairro: str | None = None,
        numero: str | None = None,
        complemento: str | None = None,
        nova_senha: str | None = None,
        confirmacao_nova_senha: str | None = None,
    ):
        if cpf is not None and usuario.cpf and cpf != usuario.cpf:
            raise CampoImutavelErro("O CPF é o único que não pode ser e nem deve ser modificado após o cadastro.")

        modificacoes = {}

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

        if cep is not None:
            cep_valido = validar_cep(cep)
            if cep_valido != usuario.cep:
                modificacoes["cep"] = (usuario.cep, cep_valido)
                usuario.cep = cep_valido

        if logradouro is not None:
            usuario.logradouro = logradouro[:100]
        if bairro is not None:
            usuario.bairro = bairro[:100]
        if numero is not None:
            usuario.numero = numero[:10]
        if complemento is not None:
            usuario.complemento = complemento[:100]

        if nova_senha:
            validar_senha(nova_senha, confirmacao_nova_senha)
            usuario.set_password(nova_senha)
            modificacoes["senha"] = "Senha alterada"

        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=usuario.cpf or usuario.username,
            operador=operador,
            identificador_operador=getattr(operador, "matricula_funcional", None) or getattr(operador, "cpf", None) or operador.username,
            cargo_operador=getattr(operador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.ALTERACAO_CADASTRO,
            detalhes={"campos_alterados": list(modificacoes.keys())},
        )
        return usuario

    @staticmethod
    @transaction.atomic
    def anonimizar(usuario, operador):
        cpf_original = usuario.cpf
        usuario.nome_completo = "Cidadão Anonimizado"
        usuario.cpf = None
        usuario.telefone = ""
        usuario.email = f"anonimizado_{usuario.pk}@maisluz.maceio.al.gov.br"
        usuario.logradouro = "Anonimizado"
        usuario.bairro = "Anonimizado"
        usuario.numero = "S/N"
        usuario.complemento = ""
        usuario.cep = "00000000"
        usuario.anonimizado = True
        usuario.status_acesso = StatusAcesso.INATIVO
        usuario.is_active = False
        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=cpf_original or f"Usuario #{usuario.pk}",
            operador=operador,
            identificador_operador=getattr(operador, "matricula_funcional", None) or getattr(operador, "cpf", None) or operador.username,
            cargo_operador=getattr(operador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.EXCLUSAO_LOGICA_CIDADAO,
            detalhes={"acao": "Exclusão lógica com anonimização conforme LGPD"},
        )
        return usuario
