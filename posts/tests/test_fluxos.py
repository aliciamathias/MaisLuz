from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Comentario, Post


class FluxosCompletosTests(TestCase):
    """Critérios de conclusão do PRD, exercitados apenas pelas rotas."""

    def test_ciclo_completo_do_autor(self):
        senha = "senha-de-teste-123"
        get_user_model().objects.create_user("autora", password=senha)

        self.client.post(reverse("contas:entrar"), {"username": "autora", "password": senha})
        self.client.post(reverse("posts:criar"), {"titulo": "Meu post", "conteudo": "Texto"})
        post = Post.objects.get()
        url_publica = reverse("posts:detalhe", args=[post.slug])
        self.assertEqual(self.client.get(url_publica).status_code, 404)

        self.client.post(reverse("posts:publicar", args=[post.pk]))
        self.assertEqual(self.client.get(url_publica).status_code, 200)

        self.client.post(
            reverse("posts:editar", args=[post.pk]),
            {"titulo": "Título novo", "conteudo": "Texto novo"},
        )
        self.assertContains(self.client.get(url_publica), "Título novo")

        self.client.post(reverse("posts:despublicar", args=[post.pk]))
        self.assertEqual(self.client.get(url_publica).status_code, 404)

        self.client.post(reverse("posts:excluir", args=[post.pk]))
        self.assertFalse(Post.objects.exists())

        self.client.post(reverse("contas:sair"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_comentario_so_aparece_depois_da_aprovacao_no_admin(self):
        usuarios = get_user_model().objects
        autor = usuarios.create_user("autora")
        self.client.force_login(autor)
        self.client.post(reverse("posts:criar"), {"titulo": "Meu post", "conteudo": "Texto"})
        post = Post.objects.get()
        self.client.post(reverse("posts:publicar", args=[post.pk]))
        self.client.post(reverse("contas:sair"))
        url_publica = reverse("posts:detalhe", args=[post.slug])

        self.client.post(
            reverse("posts:comentar", args=[post.slug]),
            {"nome": "Visitante", "texto": "Gostei muito"},
        )
        self.assertNotContains(self.client.get(url_publica), "Gostei muito")

        self.client.force_login(usuarios.create_superuser("admin"))
        self.client.post(
            reverse("admin:posts_comentario_changelist"),
            {"action": "aprovar_selecionados", "_selected_action": [Comentario.objects.get().pk]},
        )
        self.client.logout()

        self.assertContains(self.client.get(url_publica), "Gostei muito")
