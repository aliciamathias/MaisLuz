from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from posts.exceptions import PostNaoEncontrado
from posts.forms import ComentarioForm
from posts.services import ComentarioService, PostService


class ComentarioCreateView(View):
    def post(self, request, slug):
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                ComentarioService.criar(slug=slug, **form.cleaned_data)
            except PostNaoEncontrado as exc:
                raise Http404 from exc
            messages.success(request, "Comentário enviado. Ele aparecerá após a moderação.")
            return redirect("posts:detalhe", slug=slug)

        try:
            post = PostService.obter_publicado(slug)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        contexto = {
            "post": post,
            "comentarios": ComentarioService.listar_aprovados(post),
            "form": form,
        }
        return render(request, "posts/detalhe.html", contexto)
