from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View


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
            return redirect("posts:painel")
        contexto = {
            "form": AuthenticationForm(request),
            "next": _destino_seguro(request, request.GET.get("next")),
        }
        return render(request, "contas/entrar.html", contexto)

    def post(self, request) -> HttpResponse:
        destino = _destino_seguro(request, request.POST.get("next"))
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            return render(request, "contas/entrar.html", {"form": form, "next": destino})
        login(request, form.get_user())
        # HttpResponseRedirect, e não redirect(): redirect() tentaria resolver um
        # `next` sem barra como nome de rota e falharia com NoReverseMatch.
        return HttpResponseRedirect(destino or reverse("posts:painel"))
