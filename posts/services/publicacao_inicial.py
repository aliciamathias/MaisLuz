from django.contrib.auth import get_user_model
from django.db import transaction

from posts.exceptions import AutorNaoEncontrado
from posts.models import Post
from posts.publicacoes_iniciais import PUBLICACOES_INICIAIS

from .post import PostService


class PublicacaoInicialService:
    @staticmethod
    @transaction.atomic
    def criar_publicacoes(username: str) -> int:
        autor = get_user_model().objects.filter(username=username).first()
        if autor is None:
            raise AutorNaoEncontrado(username)

        quantidade = 0
        for publicacao in PUBLICACOES_INICIAIS:
            if Post.objects.filter(titulo=publicacao["titulo"]).exists():
                continue
            post = PostService.criar(autor=autor, **publicacao)
            PostService.publicar(post.pk, autor)
            quantidade += 1
        return quantidade
