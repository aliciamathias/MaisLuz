from django.contrib.auth import get_user_model
from django.db import transaction
from contas.exceptions import JustificativaObrigatoriaErro, PermissaoNegadaErro
from contas.models import HistoricoAuditoria, StatusAcesso, TipoOperacaoAuditoria

Usuario = get_user_model()


class BloqueioService:
    @staticmethod
    @transaction.atomic
    def bloquear_usuario(usuario_alvo, administrador, justificativa: str):
        if not getattr(administrador, "is_administrador", False):
            raise PermissaoNegadaErro("O acesso a esta funcionalidade é restrito exclusivamente a usuários com cargo de Administrador.")

        justificativa_limpa = (justificativa or "").strip()
        if not justificativa_limpa:
            raise JustificativaObrigatoriaErro("O motivo do bloqueio é obrigatório.")

        usuario_alvo.status_acesso = StatusAcesso.BLOQUEADO
        usuario_alvo.is_active = False
        usuario_alvo.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario_alvo,
            identificador_afetado=usuario_alvo.cpf or usuario_alvo.matricula_funcional or usuario_alvo.username,
            operador=administrador,
            identificador_operador=getattr(administrador, "matricula_funcional", None) or getattr(administrador, "cpf", None) or administrador.username,
            cargo_operador=getattr(administrador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.BLOQUEIO_CONTA,
            justificativa=justificativa_limpa,
            detalhes={"acao": "Bloqueio de conta por Administrador", "sessao_encerrada": True},
        )
        return usuario_alvo

    @staticmethod
    @transaction.atomic
    def desbloquear_usuario(usuario_alvo, administrador, justificativa: str):
        if not getattr(administrador, "is_administrador", False):
            raise PermissaoNegadaErro("O acesso a esta funcionalidade é restrito exclusivamente a usuários com cargo de Administrador.")

        justificativa_limpa = (justificativa or "").strip()
        if not justificativa_limpa:
            raise JustificativaObrigatoriaErro("A justificativa de reativação é obrigatória.")

        usuario_alvo.status_acesso = StatusAcesso.ATIVO
        usuario_alvo.is_active = True
        usuario_alvo.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=usuario_alvo,
            identificador_afetado=usuario_alvo.cpf or usuario_alvo.matricula_funcional or usuario_alvo.username,
            operador=administrador,
            identificador_operador=getattr(administrador, "matricula_funcional", None) or getattr(administrador, "cpf", None) or administrador.username,
            cargo_operador=getattr(administrador, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.DESBLOQUEIO_CONTA,
            justificativa=justificativa_limpa,
            detalhes={"acao": "Reativação de conta por Administrador"},
        )
        return usuario_alvo
