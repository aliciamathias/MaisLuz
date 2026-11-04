from collections.abc import Iterable

from django.db.models import QuerySet

from posts.models import Comentario, Post

from .post import PostService


class ComentarioService:
    @staticmethod
    def listar_aprovados(post: Post) -> QuerySet[Comentario]:
        return Comentario.objects.filter(post=post, aprovado=True).order_by("criado_em", "id")

    @staticmethod
    def criar(slug: str, nome: str, texto: str) -> Comentario:
        post = PostService.obter_publicado(slug)
        return Comentario.objects.create(post=post, nome=nome, texto=texto)

    @staticmethod
    def aprovar(comentario_ids: Iterable[int]) -> int:
        # Filtrar os pendentes faz o retorno contar apenas o que de fato mudou.
        return Comentario.objects.filter(pk__in=comentario_ids, aprovado=False).update(aprovado=True)
