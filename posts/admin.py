from django.contrib import admin, messages
from django.utils.text import Truncator

from .models import Comentario, Post
from .services import ComentarioService


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["titulo", "autor", "status", "publicado_em"]
    list_filter = ["status"]
    search_fields = ["titulo"]
    list_select_related = ["autor"]

    # Gravar por aqui ignoraria as regras do PostService.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ["nome", "post", "inicio_do_texto", "aprovado", "criado_em"]
    list_filter = ["aprovado"]
    list_select_related = ["post"]
    actions = ["aprovar_selecionados"]
    # Os campos são somente leitura, em vez de has_change_permission retornar False,
    # porque a ação de moderação depende da permissão de alteração.
    readonly_fields = ["post", "nome", "texto", "aprovado", "criado_em"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="texto")
    def inicio_do_texto(self, obj: Comentario) -> str:
        return Truncator(obj.texto).chars(60)

    @admin.action(description="Aprovar selecionados", permissions=["change"])
    def aprovar_selecionados(self, request, queryset):
        ids = list(queryset.values_list("pk", flat=True))
        quantidade = ComentarioService.aprovar(ids)
        self.message_user(request, f"Comentários aprovados: {quantidade}.", messages.SUCCESS)
