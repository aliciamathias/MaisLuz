from django.shortcuts import render
from django.views import View


class PainelOcorrenciasView(View):
    """Exibe o painel corporativo de ocorrências (Atendente e Administrador)."""

    def get(self, request):
        is_admin = (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_staff)
        )
        contexto = {
            'nav_ativa': 'ocorrencias',
            'is_admin': is_admin,
            'perfil': 'administrador' if is_admin else 'atendente',
        }
        return render(request, 'ocorrencias/ocorrencias-atendente.html', contexto)


class CadastroAtendenteView(View):
    """Exibe o formulário de cadastro e listagem de atendentes (Administrador)."""

    def get(self, request):
        contexto = {
            'nav_ativa': 'funcionarios',
            'subnav_ativa': 'listagem',
            'is_admin': True,
            'perfil': 'administrador',
        }
        return render(request, 'funcionarios/cadastro-atendente.html', contexto)


class RegistrarOcorrenciaView(View):
    """Exibe o fluxo de registro de nova ocorrência (Cidadão)."""

    def get(self, request):
        contexto = {}
        return render(request, 'ocorrencias/registrar-ocorrencia-cidadao.html', contexto)
