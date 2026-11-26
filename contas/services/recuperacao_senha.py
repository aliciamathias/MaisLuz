from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from contas.exceptions import (
    CredenciaisRecuperacaoInvalidasErro,
    PermissaoNegadaErro,
)
from contas.models import (
    HistoricoAuditoria,
    SolicitacaoRecuperacaoSenha,
    StatusSolicitacao,
    TipoOperacaoAuditoria,
    TipoPerfil,
)
from .validadores import validar_cpf, validar_senha, validar_telefone

Usuario = get_user_model()


class RecuperacaoSenhaService:
    @staticmethod
    @transaction.atomic
    def solicitar_recuperacao(cpf: str, telefone: str):
        cpf_valido = validar_cpf(cpf)
        tel_valido = validar_telefone(telefone)

        usuario = Usuario.objects.filter(cpf=cpf_valido, telefone=tel_valido).first()
        if not usuario:
            raise CredenciaisRecuperacaoInvalidasErro(
                "CPF ou telefone não correspondem a uma conta cadastrada"
            )

        if usuario.tipo_perfil == TipoPerfil.CIDADAO:
            HistoricoAuditoria.objects.create(
                usuario_afetado=usuario,
                identificador_afetado=cpf_valido,
                operador=usuario,
                identificador_operador=cpf_valido,
                tipo_operacao=TipoOperacaoAuditoria.SOLICITACAO_RECUPERACAO_SENHA,
                detalhes={"tipo_conta": "CIDADAO", "etapa": "Início da redefinição direta"},
            )
            return {
                "tipo": "CIDADAO",
                "usuario": usuario,
                "mensagem": "Conta de cidadão identificada. Prossiga para redefinição.",
            }

        # Funcionário: não permite redefinição direta sem aprovação
        solicitacao = SolicitacaoRecuperacaoSenha.objects.create(
            funcionario=usuario,
            status=StatusSolicitacao.PENDENTE,
        )

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=usuario.matricula_funcional or cpf_valido,
            operador=usuario,
            identificador_operador=usuario.matricula_funcional or cpf_valido,
            tipo_operacao=TipoOperacaoAuditoria.SOLICITACAO_RECUPERACAO_SENHA,
            detalhes={
                "tipo_conta": "FUNCIONARIO",
                "solicitacao_id": solicitacao.pk,
                "mensagem": "Solicitação enviada para autorização do Administrador",
            },
        )

        return {
            "tipo": "FUNCIONARIO",
            "usuario": usuario,
            "solicitacao": solicitacao,
            "mensagem": "Solicitação enviada para autorização do Administrador",
        }

    @staticmethod
    @transaction.atomic
    def redefinir_senha_cidadao(usuario, nova_senha: str, confirmacao_senha: str):
        validar_senha(nova_senha, confirmacao_senha)
        usuario.set_password(nova_senha)
        usuario.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario,
            identificador_afetado=usuario.cpf or usuario.username,
            operador=usuario,
            identificador_operador=usuario.cpf or usuario.username,
            tipo_operacao=TipoOperacaoAuditoria.REDEFINICAO_SENHA_CONCLUIDA,
            detalhes={"acao": "Senha de cidadão redefinida com sucesso"},
        )
        return usuario

    @staticmethod
    @transaction.atomic
    def avaliar_solicitacao_funcionario(
        solicitacao: SolicitacaoRecuperacaoSenha,
        administrador,
        aprovar: bool,
        motivo_rejeicao: str = "",
        nova_senha: str | None = None,
    ):
        if not getattr(administrador, "is_administrador", False):
            raise PermissaoNegadaErro("Apenas Administradores podem avaliar solicitações de senha de funcionários.")

        solicitacao.aprovado_por = administrador
        solicitacao.data_analise = timezone.now()

        if aprovar:
            solicitacao.status = StatusSolicitacao.APROVADA
            if nova_senha:
                validar_senha(nova_senha)
                funcionario = solicitacao.funcionario
                funcionario.set_password(nova_senha)
                funcionario.save()
        else:
            solicitacao.status = StatusSolicitacao.REJEITADA
            solicitacao.motivo_rejeicao = motivo_rejeicao

        solicitacao.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=solicitacao.funcionario,
            identificador_afetado=solicitacao.funcionario.matricula_funcional or solicitacao.funcionario.username,
            operador=administrador,
            identificador_operador=getattr(administrador, "matricula_funcional", None) or administrador.username,
            cargo_operador=getattr(administrador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.REDEFINICAO_SENHA_CONCLUIDA if aprovar else TipoOperacaoAuditoria.SOLICITACAO_RECUPERACAO_SENHA,
            justificativa=motivo_rejeicao,
            detalhes={"solicitacao_id": solicitacao.pk, "status": solicitacao.status},
        )
        return solicitacao
