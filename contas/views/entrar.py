from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from contas.forms import LoginForm


def _destino_seguro(request: HttpRequest, destino: str | None) -> str | None:
    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino
    return None


class EntrarView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if getattr(request.user, "is_cidadao", False):
                return redirect("minhas_ocorrencias")
            return redirect("ocorrencias_painel")

        contexto = {
            "form": LoginForm(request),
            "next": _destino_seguro(request, request.GET.get("next")),
            "header_variante": "login",
        }
        return render(request, "contas/entrar.html", contexto)

    def post(self, request) -> HttpResponse:
        destino = _destino_seguro(request, request.POST.get("next"))
        form = LoginForm(request, data=request.POST)
        if not form.is_valid():
            return render(
                request,
                "contas/entrar.html",
                {"form": form, "next": destino, "header_variante": "login"},
            )

        user = form.get_user()
        login(request, user)
        messages.success(request, "Login realizado com sucesso!")

        if destino:
            return HttpResponseRedirect(destino)

        if getattr(user, "is_cidadao", False):
            return HttpResponseRedirect(reverse("minhas_ocorrencias"))
        return HttpResponseRedirect(reverse("ocorrencias_painel"))
