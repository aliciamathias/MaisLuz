from django.conf import settings
from django.db import models


class StatusSolicitacao(models.TextChoices):
    PENDENTE = 'PENDENTE', 'Pendente'
    APROVADA = 'APROVADA', 'Aprovada'
    REJEITADA = 'REJEITADA', 'Rejeitada'


class SolicitacaoRecuperacaoSenha(models.Model):
    funcionario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='solicitacoes_recuperacao_senha',
    )
    status = models.CharField(
        max_length=20,
        choices=StatusSolicitacao.choices,
        default=StatusSolicitacao.PENDENTE,
        db_index=True,
    )
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_senha_avaliadas',
    )
    motivo_rejeicao = models.TextField(blank=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True, db_index=True)
    data_analise = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_solicitacao']
        verbose_name = 'Solicitação de Recuperação de Senha'
        verbose_name_plural = 'Solicitações de Recuperação de Senha'

    def __str__(self):
        return f"Solicitação #{self.pk} - {self.funcionario} ({self.status})"
