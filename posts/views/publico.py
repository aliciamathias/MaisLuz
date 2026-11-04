from django.http import Http404
from django.shortcuts import render
from django.views import View

from posts.exceptions import PostNaoEncontrado
from posts.forms import ComentarioForm
from posts.services import ComentarioService, PostService


class PostListView(View):
    def get(self, request):
        posts = PostService.listar_publicados(request.GET.get("pagina", 1))
        return render(request, "posts/lista.html", {"posts": posts})


class PostDetailView(View):
    def get(self, request, slug):
        try:
            post = PostService.obter_publicado(slug)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        contexto = {
            "post": post,
            "comentarios": ComentarioService.listar_aprovados(post),
            "form": ComentarioForm(),
        }
        return render(request, "posts/detalhe.html", contexto)
