from django.contrib import admin
from django.urls import include, path

from core.views import (
    CadastroAtendenteView,
    PainelOcorrenciasView,
    RegistrarOcorrenciaView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RegistrarOcorrenciaView.as_view(), name='inicio'),
    path('ocorrencias/registrar/', RegistrarOcorrenciaView.as_view(), name='registrar_ocorrencia'),
    path('ocorrencias/painel/', PainelOcorrenciasView.as_view(), name='ocorrencias_painel'),
    path('funcionarios/cadastro/', CadastroAtendenteView.as_view(), name='cadastro_atendente'),
    path('', include('contas.urls')),
]
