from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from posts.models import Comentario, Post
from posts.services import PostService


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuarios = get_user_model().objects
        cls.admin = usuarios.create_superuser("admin")
        cls.autor = usuarios.create_user("autora")
        cls.post = PostService.criar(cls.autor, "Título", "Conteúdo")
        PostService.publicar(cls.post.pk, cls.autor)
        cls.comentario = Comentario.objects.create(post=cls.post, nome="Ana", texto="Texto original")
        cls.url_lista = reverse("admin:posts_comentario_changelist")

    def setUp(self):
        self.client.force_login(self.admin)

    def _aplicar_acao(self, acao="aprovar_selecionados"):
        return self.client.post(
            self.url_lista,
            {"action": acao, "_selected_action": [self.comentario.pk]},
        )


class PostAdminTests(AdminTestCase):
    def test_listagem_e_visualizacao_funcionam(self):
        lista = self.client.get(reverse("admin:posts_post_changelist"))
        detalhe = self.client.get(reverse("admin:posts_post_change", args=[self.post.pk]))

        self.assertEqual(lista.status_code, 200)
        self.assertEqual(detalhe.status_code, 200)

    def test_post_e_somente_leitura(self):
        id_do_post = self.post.pk
        adicionar = self.client.post(reverse("admin:posts_post_add"), {})
        alterar = self.client.post(
            reverse("admin:posts_post_change", args=[id_do_post]),
            {"titulo": "Alterado"},
        )
        excluir = self.client.post(reverse("admin:posts_post_delete", args=[id_do_post]), {"post": "yes"})

        self.assertEqual(adicionar.status_code, 403)
        self.assertEqual(alterar.status_code, 403)
        self.assertEqual(excluir.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.titulo, "Título")


class ComentarioAdminTests(AdminTestCase):
    def test_listagem_mostra_dados_da_moderacao(self):
        resposta = self.client.get(self.url_lista, {"aprovado__exact": 0})

        self.assertContains(resposta, "Ana")
        self.assertContains(resposta, "Texto original")

    def test_acao_aprova_os_selecionados(self):
        resposta = self._aplicar_acao()

        self.assertRedirects(resposta, self.url_lista)
        self.comentario.refresh_from_db()
        self.assertTrue(self.comentario.aprovado)

    def test_acao_exige_permissao_de_alteracao(self):
        moderador = get_user_model().objects.create_user("leitor", is_staff=True)
        moderador.user_permissions.add(Permission.objects.get(codename="view_comentario"))
        self.client.force_login(moderador)

        self._aplicar_acao()

        self.comentario.refresh_from_db()
        self.assertFalse(self.comentario.aprovado)

    def test_nao_e_possivel_adicionar_comentario(self):
        resposta = self.client.get(reverse("admin:posts_comentario_add"))

        self.assertEqual(resposta.status_code, 403)

    def test_campos_nao_sao_editaveis(self):
        url = reverse("admin:posts_comentario_change", args=[self.comentario.pk])

        self.client.post(url, {"nome": "Outro", "texto": "Alterado", "aprovado": "on"})

        self.comentario.refresh_from_db()
        self.assertEqual(self.comentario.nome, "Ana")
        self.assertEqual(self.comentario.texto, "Texto original")
        self.assertFalse(self.comentario.aprovado)

    def test_exclusao_continua_disponivel(self):
        url = reverse("admin:posts_comentario_delete", args=[self.comentario.pk])

        self.client.post(url, {"post": "yes"})

        self.assertFalse(Comentario.objects.exists())
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
