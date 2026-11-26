from django.conf import settings
from django.db import models


class TipoDefeito(models.TextChoices):
    POSTE_APAGADO = 'Poste Apagado', 'Poste Apagado'
    LUZ_OSCILANDO = 'Luz Oscilando', 'Luz Oscilando'
    ESTRUTURA_DANIFICADA = 'Estrutura Danificada', 'Estrutura Danificada'


class StatusOcorrencia(models.TextChoices):
    PENDENTE = 'Pendente', 'Pendente'
    EM_PROGRESSO = 'Em progresso', 'Em progresso'
    CONCLUIDO = 'Concluído', 'Concluído'
    EXCLUIDO_CIDADAO = 'Excluído pelo Cidadão', 'Excluído pelo Cidadão'
    EXCLUIDO_FUNCIONARIO = 'Excluído pelo Funcionário', 'Excluído pelo Funcionário'


class Ocorrencia(models.Model):
    protocolo = models.CharField(max_length=10, unique=True, db_index=True)
    numero_poste = models.CharField(max_length=10, db_index=True)
    cidadao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ocorrencias',
    )
    atendente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ocorrencias_atendidas',
    )
    cpf_cidadao_snapshot = models.CharField(max_length=14, blank=True)
    nome_cidadao_snapshot = models.CharField(max_length=120, blank=True)
    logradouro = models.CharField(max_length=100)
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100, db_index=True)
    ponto_referencia = models.CharField(max_length=200)
    tipo_defeito = models.CharField(max_length=50, choices=TipoDefeito.choices)
    descricao = models.CharField(max_length=300, blank=True)
    foto = models.FileField(upload_to='ocorrencias/', blank=True, null=True)
    status = models.CharField(
        max_length=35,
        choices=StatusOcorrencia.choices,
        default=StatusOcorrencia.PENDENTE,
        db_index=True,
    )
    data_registro = models.DateTimeField(auto_now_add=True, db_index=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_registro']
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'

    def __str__(self):
        return f"Protocolo #{self.protocolo} - Poste {self.numero_poste} ({self.status})"
