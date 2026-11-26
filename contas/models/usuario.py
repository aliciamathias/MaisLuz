from django.contrib.auth.models import AbstractUser
from django.db import models


class TipoPerfil(models.TextChoices):
    CIDADAO = 'CIDADAO', 'Cidadão'
    FUNCIONARIO = 'FUNCIONARIO', 'Funcionário'


class CargoFuncionario(models.TextChoices):
    ADMINISTRADOR = 'Administrador', 'Administrador'
    GESTOR_SISTEMA = 'Gestor de Sistema', 'Gestor de Sistema'
    GESTOR_OCORRENCIAS = 'Gestor de Ocorrências', 'Gestor de Ocorrências'
    ATENDENTE = 'Atendente', 'Atendente'


class StatusAcesso(models.TextChoices):
    ATIVO = 'ATIVO', 'Ativo'
    BLOQUEADO = 'BLOQUEADO', 'Bloqueado'
    INATIVO = 'INATIVO', 'Inativo'


class Usuario(AbstractUser):
    nome_completo = models.CharField(max_length=120, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True, db_index=True)
    telefone = models.CharField(max_length=14, blank=True)
    tipo_perfil = models.CharField(
        max_length=20,
        choices=TipoPerfil.choices,
        default=TipoPerfil.CIDADAO,
        db_index=True,
    )
    status_acesso = models.CharField(
        max_length=20,
        choices=StatusAcesso.choices,
        default=StatusAcesso.ATIVO,
        db_index=True,
    )
    anonimizado = models.BooleanField(default=False)

    # Endereço (Cidadão)
    cep = models.CharField(max_length=8, blank=True)
    logradouro = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    complemento = models.CharField(max_length=100, blank=True)

    # Identificação profissional (Funcionário)
    matricula_funcional = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    cargo = models.CharField(max_length=60, blank=True, choices=CargoFuncionario.choices)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        identificador = self.cpf or self.matricula_funcional or self.username
        return f"{self.nome_completo or self.username} ({identificador})"

    @property
    def is_cidadao(self) -> bool:
        return self.tipo_perfil == TipoPerfil.CIDADAO

    @property
    def is_funcionario(self) -> bool:
        return self.tipo_perfil == TipoPerfil.FUNCIONARIO

    @property
    def is_administrador(self) -> bool:
        return (
            self.is_superuser
            or (self.is_funcionario and self.cargo == CargoFuncionario.ADMINISTRADOR)
        )

    @property
    def is_gestor_sistema(self) -> bool:
        return self.is_administrador or (
            self.is_funcionario and self.cargo == CargoFuncionario.GESTOR_SISTEMA
        )

    @property
    def is_bloqueado(self) -> bool:
        return self.status_acesso == StatusAcesso.BLOQUEADO
