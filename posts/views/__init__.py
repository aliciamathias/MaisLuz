from .comentario import ComentarioCreateView
from .painel import (
    PainelView,
    PostCreateView,
    PostDeleteView,
    PostDespublicarView,
    PostPublicarView,
    PostUpdateView,
)
from .publico import PostDetailView, PostListView

__all__ = [
    "ComentarioCreateView",
    "PainelView",
    "PostCreateView",
    "PostDeleteView",
    "PostDespublicarView",
    "PostDetailView",
    "PostListView",
    "PostPublicarView",
    "PostUpdateView",
]
