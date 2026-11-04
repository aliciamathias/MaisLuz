from django.urls import path

from .views import EntrarView, SairView

app_name = "contas"

urlpatterns = [
    path("entrar/", EntrarView.as_view(), name="entrar"),
    path("sair/", SairView.as_view(), name="sair"),
]
