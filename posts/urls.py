from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListView.as_view(), name="lista"),
    path("posts/<slug:slug>/", views.PostDetailView.as_view(), name="detalhe"),
    path("posts/<slug:slug>/comentarios/", views.ComentarioCreateView.as_view(), name="comentar"),
    path("painel/", views.PainelView.as_view(), name="painel"),
    path("painel/posts/novo/", views.PostCreateView.as_view(), name="criar"),
    path("painel/posts/<int:post_id>/editar/", views.PostUpdateView.as_view(), name="editar"),
    path("painel/posts/<int:post_id>/excluir/", views.PostDeleteView.as_view(), name="excluir"),
    path("painel/posts/<int:post_id>/publicar/", views.PostPublicarView.as_view(), name="publicar"),
    path(
        "painel/posts/<int:post_id>/despublicar/",
        views.PostDespublicarView.as_view(),
        name="despublicar",
    ),
]
