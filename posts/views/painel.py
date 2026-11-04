from django.contrib import messages
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from posts.exceptions import PostNaoEncontrado
from posts.forms import PostForm
from posts.models import Post
from posts.services import PostService


def _obter_do_autor_ou_404(post_id: int, autor: AbstractBaseUser) -> Post:
    try:
        return PostService.obter_do_autor(post_id, autor)
    except PostNaoEncontrado as exc:
        raise Http404 from exc


class PainelView(LoginRequiredMixin, View):
    def get(self, request):
        posts = PostService.listar_do_autor(request.user, request.GET.get("pagina", 1))
        return render(request, "posts/painel.html", {"posts": posts})


class PostCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "posts/form.html", {"form": PostForm(), "titulo_pagina": "Novo post"})

    def post(self, request):
        form = PostForm(request.POST)
        if not form.is_valid():
            return render(request, "posts/form.html", {"form": form, "titulo_pagina": "Novo post"})
        PostService.criar(autor=request.user, **form.cleaned_data)
        messages.success(request, "Rascunho criado.")
        return redirect("posts:painel")


class PostUpdateView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = _obter_do_autor_ou_404(post_id, request.user)
        contexto = {"form": PostForm(instance=post), "titulo_pagina": "Editar post"}
        return render(request, "posts/form.html", contexto)

    def post(self, request, post_id):
        # A posse é verificada antes da validação: dados inválidos enviados para o
        # post de outro autor também precisam resultar em 404.
        post = _obter_do_autor_ou_404(post_id, request.user)
        form = PostForm(request.POST, instance=post)
        if not form.is_valid():
            return render(request, "posts/form.html", {"form": form, "titulo_pagina": "Editar post"})
        try:
            PostService.atualizar(post_id=post_id, autor=request.user, **form.cleaned_data)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        messages.success(request, "Post atualizado.")
        return redirect("posts:painel")


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = _obter_do_autor_ou_404(post_id, request.user)
        return render(request, "posts/confirmar_exclusao.html", {"post": post})

    def post(self, request, post_id):
        try:
            PostService.excluir(post_id, request.user)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        messages.success(request, "Post excluído.")
        return redirect("posts:painel")


class PostPublicarView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        try:
            PostService.publicar(post_id, request.user)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        messages.success(request, "Post publicado.")
        return redirect("posts:painel")


class PostDespublicarView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        try:
            PostService.despublicar(post_id, request.user)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        messages.success(request, "Post voltou para rascunho.")
        return redirect("posts:painel")
