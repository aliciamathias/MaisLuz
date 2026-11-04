from django.contrib.auth.base_user import AbstractBaseUser
from django.core.paginator import Page, Paginator
from django.utils import timezone
from django.utils.text import slugify

from posts.exceptions import PostNaoEncontrado
from posts.models import Post, StatusPost

POSTS_POR_PAGINA = 10
LIMITE_BASE_SLUG = 200
BASE_SLUG_PADRAO = "post"


def _gerar_slug(titulo: str) -> str:
    # O corte pode deixar um separador no fim, que geraria "titulo--2" com o sufixo.
    base = slugify(titulo)[:LIMITE_BASE_SLUG].rstrip("-_") or BASE_SLUG_PADRAO
    slug = base
    sufixo = 2
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base}-{sufixo}"
        sufixo += 1
    return slug


class PostService:
    @staticmethod
    def listar_publicados(pagina: int | str = 1) -> Page:
        # O id desempata posts com a mesma data, para que a paginação seja estável.
        posts = (
            Post.objects.filter(status=StatusPost.PUBLICADO)
            .select_related("autor")
            .order_by("-publicado_em", "-id")
        )
        return Paginator(posts, POSTS_POR_PAGINA).get_page(pagina)

    @staticmethod
    def obter_publicado(slug: str) -> Post:
        try:
            return Post.objects.select_related("autor").get(slug=slug, status=StatusPost.PUBLICADO)
        except Post.DoesNotExist as exc:
            raise PostNaoEncontrado(slug) from exc

    @staticmethod
    def listar_do_autor(autor: AbstractBaseUser, pagina: int | str = 1) -> Page:
        posts = Post.objects.filter(autor=autor).order_by("-criado_em", "-id")
        return Paginator(posts, POSTS_POR_PAGINA).get_page(pagina)

    @staticmethod
    def obter_do_autor(post_id: int, autor: AbstractBaseUser) -> Post:
        try:
            return Post.objects.get(pk=post_id, autor=autor)
        except Post.DoesNotExist as exc:
            raise PostNaoEncontrado(post_id) from exc

    @staticmethod
    def criar(autor: AbstractBaseUser, titulo: str, conteudo: str) -> Post:
        return Post.objects.create(
            autor=autor,
            titulo=titulo,
            conteudo=conteudo,
            slug=_gerar_slug(titulo),
        )

    @staticmethod
    def atualizar(post_id: int, autor: AbstractBaseUser, titulo: str, conteudo: str) -> Post:
        post = PostService.obter_do_autor(post_id, autor)
        post.titulo = titulo
        post.conteudo = conteudo
        post.save(update_fields=["titulo", "conteudo", "atualizado_em"])
        return post

    @staticmethod
    def publicar(post_id: int, autor: AbstractBaseUser) -> Post:
        post = PostService.obter_do_autor(post_id, autor)
        if post.status == StatusPost.PUBLICADO:
            return post
        post.status = StatusPost.PUBLICADO
        if post.publicado_em is None:
            post.publicado_em = timezone.now()
        post.save(update_fields=["status", "publicado_em", "atualizado_em"])
        return post

    @staticmethod
    def despublicar(post_id: int, autor: AbstractBaseUser) -> Post:
        post = PostService.obter_do_autor(post_id, autor)
        if post.status == StatusPost.RASCUNHO:
            return post
        post.status = StatusPost.RASCUNHO
        post.save(update_fields=["status", "atualizado_em"])
        return post

    @staticmethod
    def excluir(post_id: int, autor: AbstractBaseUser) -> None:
        PostService.obter_do_autor(post_id, autor).delete()
