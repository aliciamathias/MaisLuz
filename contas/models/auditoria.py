from django.conf import settings
from django.db import models


class TipoOperacaoAuditoria(models.TextChoices):
    CADASTRO_CIDADAO = 'CADASTRO_CIDADAO', 'Cadastro de Cidadão'
    CADASTRO_FUNCIONARIO = 'CADASTRO_FUNCIONARIO', 'Cadastro de Funcionário'
    ALTERACAO_CADASTRO = 'ALTERACAO_CADASTRO', 'Alteração de Dados Cadastrais'
    EXCLUSAO_LOGICA_CIDADAO = 'EXCLUSAO_LOGICA_CIDADAO', 'Exclusão Lógica e Anonimização de Cidadão'
    INATIVACAO_FUNCIONARIO = 'INATIVACAO_FUNCIONARIO', 'Inativação de Funcionário'
    BLOQUEIO_CONTA = 'BLOQUEIO_CONTA', 'Bloqueio de Conta por Administrador'
    DESBLOQUEIO_CONTA = 'DESBLOQUEIO_CONTA', 'Desbloqueio de Conta por Administrador'
    SOLICITACAO_RECUPERACAO_SENHA = 'SOLICITACAO_RECUPERACAO_SENHA', 'Solicitação de Recuperação de Senha'
    REDEFINICAO_SENHA_CONCLUIDA = 'REDEFINICAO_SENHA_CONCLUIDA', 'Redefinição de Senha Concluída'
    EXCLUSAO_OCORRENCIA_CIDADAO = 'EXCLUSAO_OCORRENCIA_CIDADAO', 'Exclusão Lógica de Ocorrência por Cidadão'
    EXCLUSAO_OCORRENCIA_FUNCIONARIO = 'EXCLUSAO_OCORRENCIA_FUNCIONARIO', 'Exclusão Lógica de Ocorrência por Funcionário'
    ATUALIZACAO_STATUS_OCORRENCIA = 'ATUALIZACAO_STATUS_OCORRENCIA', 'Atualização de Status de Ocorrência'


class HistoricoAuditoria(models.Model):
    usuario_afetado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_sofridas',
    )
    identificador_afetado = models.CharField(max_length=50, blank=True, db_index=True)
    ocorrencia = models.ForeignKey(
        'ocorrencias.Ocorrencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historicos_auditoria',
    )
    protocolo_ocorrencia = models.CharField(max_length=10, blank=True, db_index=True)
    operador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_realizadas',
    )
    identificador_operador = models.CharField(max_length=50, blank=True)
    cargo_operador = models.CharField(max_length=60, blank=True)
    tipo_operacao = models.CharField(
        max_length=60,
        choices=TipoOperacaoAuditoria.choices,
        db_index=True,
    )
    justificativa = models.TextField(blank=True)
    detalhes = models.JSONField(default=dict, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Histórico de Auditoria'
        verbose_name_plural = 'Históricos de Auditoria'

    def __str__(self):
        return f"[{self.data_hora:%d/%m/%Y %H:%M}] {self.tipo_operacao} ({self.identificador_afetado or 'N/A'})"
