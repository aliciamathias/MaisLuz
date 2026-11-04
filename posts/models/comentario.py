from django.db import models

from .post import Post


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comentarios")
    nome = models.CharField(max_length=80)
    texto = models.TextField(max_length=2000)
    aprovado = models.BooleanField(default=False)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "comentário"
        verbose_name_plural = "comentários"
        indexes = [
            models.Index(fields=["post", "aprovado", "criado_em"], name="comentario_post_aprovado_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.nome} em {self.post.titulo}"
