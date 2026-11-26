from django.contrib import admin
from django.urls import include, path

from core.views import (
    CadastroAtendenteView,
    CadastroCidadaoView,
    CadastroSucessoView,
    EditarAtendenteView,
    LandingPageView,
    MeuPerfilCidadaoView,
    MeuPerfilInternoView,
    MinhasOcorrenciasView,
    PainelOcorrenciasView,
    RecuperarSenhaAtendenteView,
    RecuperarSenhaCidadaoView,
    RegistrarOcorrenciaView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='inicio'),
    path('ocorrencias/registrar/', RegistrarOcorrenciaView.as_view(), name='registrar_ocorrencia'),
    path('ocorrencias/painel/', PainelOcorrenciasView.as_view(), name='ocorrencias_painel'),
    path('ocorrencias/minhas/', MinhasOcorrenciasView.as_view(), name='minhas_ocorrencias'),
    path('funcionarios/cadastro/', CadastroAtendenteView.as_view(), name='cadastro_atendente'),
    path('funcionarios/editar/', EditarAtendenteView.as_view(), name='editar_atendente'),
    path('perfil/', MeuPerfilInternoView.as_view(), name='meu_perfil_interno'),
    path('cidadao/cadastro/', CadastroCidadaoView.as_view(), name='cadastro_cidadao'),
    path('cidadao/cadastro/sucesso/', CadastroSucessoView.as_view(), name='cadastro_sucesso'),
    path('cidadao/perfil/', MeuPerfilCidadaoView.as_view(), name='meu_perfil_cidadao'),
    path('contas/recuperar-senha/cidadao/', RecuperarSenhaCidadaoView.as_view(), name='recuperar_senha_cidadao'),
    path('contas/recuperar-senha/atendente/', RecuperarSenhaAtendenteView.as_view(), name='recuperar_senha_atendente'),
    path('', include('contas.urls')),
]
