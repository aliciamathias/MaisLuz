from django.conf import settings
from django.db import models
from django.db.models import Q


class StatusPost(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    PUBLICADO = "PUBLICADO", "Publicado"


class Post(models.Model):
    titulo = models.CharField("título", max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    conteudo = models.TextField("conteúdo")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    status = models.CharField(
        max_length=9,
        choices=StatusPost.choices,
        default=StatusPost.RASCUNHO,
    )
    publicado_em = models.DateTimeField("publicado em", null=True, blank=True)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(status=StatusPost.PUBLICADO) | Q(publicado_em__isnull=False),
                name="post_publicado_tem_data",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "-publicado_em"], name="post_status_publicado_idx"),
        ]

    def __str__(self) -> str:
        return self.titulo
