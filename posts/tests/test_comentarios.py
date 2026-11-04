from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.exceptions import PostNaoEncontrado
from posts.models import Comentario
from posts.services import ComentarioService, PostService


class ComentarioTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.autor = get_user_model().objects.create_user("autora")
        cls.rascunho = PostService.criar(cls.autor, "Rascunho", "C")
        cls.post = PostService.criar(cls.autor, "Publicado", "C")
        PostService.publicar(cls.post.pk, cls.autor)
        cls.url_detalhe = reverse("posts:detalhe", args=[cls.post.slug])
        cls.url_comentar = reverse("posts:comentar", args=[cls.post.slug])


class ComentarioServiceTests(ComentarioTestCase):
    def test_criar_gera_comentario_pendente(self):
        comentario = ComentarioService.criar(self.post.slug, "Ana", "Oi")

        self.assertEqual(comentario.post, self.post)
        self.assertFalse(comentario.aprovado)

    def test_criar_em_rascunho_levanta_excecao(self):
        with self.assertRaises(PostNaoEncontrado):
            ComentarioService.criar(self.rascunho.slug, "Ana", "Oi")

    def test_listar_aprovados_ignora_pendentes_e_ordena_do_mais_antigo(self):
        primeiro = Comentario.objects.create(post=self.post, nome="A", texto="1", aprovado=True)
        Comentario.objects.create(post=self.post, nome="B", texto="2")
        terceiro = Comentario.objects.create(post=self.post, nome="C", texto="3", aprovado=True)

        self.assertEqual(list(ComentarioService.listar_aprovados(self.post)), [primeiro, terceiro])

    def test_aprovar_retorna_a_quantidade_alterada(self):
        pendente = Comentario.objects.create(post=self.post, nome="A", texto="1")
        aprovado = Comentario.objects.create(post=self.post, nome="B", texto="2", aprovado=True)

        quantidade = ComentarioService.aprovar([pendente.pk, aprovado.pk])

        self.assertEqual(quantidade, 1)
        pendente.refresh_from_db()
        self.assertTrue(pendente.aprovado)


class ComentarioViewTests(ComentarioTestCase):
    def test_comentario_valido_e_criado_como_pendente(self):
        resposta = self.client.post(self.url_comentar, {"nome": "Ana", "texto": "Oi"}, follow=True)

        self.assertRedirects(resposta, self.url_detalhe)
        self.assertContains(resposta, "Comentário enviado. Ele aparecerá após a moderação.")
        self.assertFalse(Comentario.objects.get().aprovado)

    def test_visitante_nao_consegue_se_aprovar_pelo_formulario(self):
        self.client.post(self.url_comentar, {"nome": "Ana", "texto": "Oi", "aprovado": "on"})

        self.assertFalse(Comentario.objects.get().aprovado)

    def test_comentario_pendente_nao_aparece_no_detalhe(self):
        Comentario.objects.create(post=self.post, nome="Ana", texto="Texto pendente")

        resposta = self.client.get(self.url_detalhe)

        self.assertNotContains(resposta, "Texto pendente")

    def test_comentario_aprovado_aparece_no_detalhe(self):
        Comentario.objects.create(post=self.post, nome="Ana", texto="Texto aprovado", aprovado=True)

        resposta = self.client.get(self.url_detalhe)

        self.assertContains(resposta, "Texto aprovado")

    def test_comentar_em_rascunho_ou_slug_inexistente_retorna_404(self):
        dados_por_caso = {"válidos": {"nome": "Ana", "texto": "Oi"}, "inválidos": {}}
        for slug in (self.rascunho.slug, "nao-existe"):
            for caso, dados in dados_por_caso.items():
                with self.subTest(slug=slug, dados=caso):
                    resposta = self.client.post(reverse("posts:comentar", args=[slug]), dados)
                    self.assertEqual(resposta.status_code, 404)
        self.assertFalse(Comentario.objects.exists())

    def test_post_invalido_mostra_erros_e_mantem_o_texto(self):
        Comentario.objects.create(post=self.post, nome="Bia", texto="Já aprovado", aprovado=True)

        resposta = self.client.post(self.url_comentar, {"nome": "", "texto": "Texto digitado"})

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "posts/detalhe.html")
        self.assertTrue(resposta.context["form"].errors["nome"])
        self.assertContains(resposta, "Texto digitado")
        self.assertContains(resposta, "Já aprovado")
        self.assertEqual(Comentario.objects.count(), 1)

    def test_texto_acima_de_2000_caracteres_e_rejeitado(self):
        resposta = self.client.post(self.url_comentar, {"nome": "Ana", "texto": "a" * 2001})

        self.assertTrue(resposta.context["form"].errors["texto"])
        self.assertFalse(Comentario.objects.exists())

    def test_texto_com_2000_caracteres_e_aceito(self):
        self.client.post(self.url_comentar, {"nome": "Ana", "texto": "a" * 2000})

        self.assertEqual(Comentario.objects.count(), 1)

    def test_get_na_rota_de_comentar_retorna_405(self):
        self.assertEqual(self.client.get(self.url_comentar).status_code, 405)

    def test_comentario_com_script_aparece_escapado(self):
        Comentario.objects.create(
            post=self.post,
            nome="<b>Ana</b>",
            texto="<script>alert(1)</script>",
            aprovado=True,
        )

        resposta = self.client.get(self.url_detalhe)

        self.assertNotContains(resposta, "<script>alert(1)</script>")
        self.assertContains(resposta, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertContains(resposta, "&lt;b&gt;Ana&lt;/b&gt;")

    def test_post_sem_token_csrf_e_rejeitado(self):
        cliente = Client(enforce_csrf_checks=True)

        resposta = cliente.post(self.url_comentar, {"nome": "Ana", "texto": "Oi"})

        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(Comentario.objects.exists())

    def test_excluir_post_exclui_seus_comentarios(self):
        Comentario.objects.create(post=self.post, nome="Ana", texto="Oi")

        self.post.delete()

        self.assertFalse(Comentario.objects.exists())
