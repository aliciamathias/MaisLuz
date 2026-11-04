from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Post, StatusPost
from posts.services import PostService


class PostViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuarios = get_user_model().objects
        cls.autor = usuarios.create_user("autora")
        cls.outro = usuarios.create_user("outra")
        cls.rascunho = PostService.criar(cls.autor, "Meu rascunho", "Texto do rascunho")
        cls.publicado = PostService.criar(cls.autor, "Meu publicado", "Texto do publicado")
        PostService.publicar(cls.publicado.pk, cls.autor)


class PaginasPublicasTests(PostViewTestCase):
    def test_pagina_inicial_mostra_dados_dos_publicados(self):
        resposta = self.client.get(reverse("posts:lista"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Meu publicado")
        self.assertContains(resposta, "autora")
        self.assertContains(resposta, "Texto do publicado")
        self.assertNotContains(resposta, "Meu rascunho")

    def test_pagina_inicial_mostra_apenas_um_trecho_do_conteudo(self):
        fim = "palavra-final"
        post = PostService.criar(self.autor, "Longo", "palavra " * 100 + fim)
        PostService.publicar(post.pk, self.autor)

        resposta = self.client.get(reverse("posts:lista"))

        self.assertNotContains(resposta, fim)

    def test_pagina_inicial_nao_quebra_com_pagina_invalida(self):
        resposta = self.client.get(reverse("posts:lista"), {"pagina": "abc"})

        self.assertEqual(resposta.status_code, 200)

    def test_pagina_inicial_navega_entre_paginas(self):
        for indice in range(11):
            post = PostService.criar(self.autor, f"Post {indice}", "C")
            PostService.publicar(post.pk, self.autor)

        primeira = self.client.get(reverse("posts:lista"))
        segunda = self.client.get(reverse("posts:lista"), {"pagina": 2})

        self.assertContains(primeira, "?pagina=2")
        self.assertContains(segunda, "Meu publicado")

    def test_detalhe_de_publicado_retorna_200(self):
        resposta = self.client.get(reverse("posts:detalhe", args=[self.publicado.slug]))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Texto do publicado")

    def test_detalhe_de_rascunho_retorna_404_inclusive_para_o_autor(self):
        url = reverse("posts:detalhe", args=[self.rascunho.slug])

        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.autor)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_conteudo_com_script_aparece_escapado_no_detalhe(self):
        post = PostService.criar(self.autor, "Script", "<script>alert(1)</script>")
        PostService.publicar(post.pk, self.autor)

        resposta = self.client.get(reverse("posts:detalhe", args=[post.slug]))

        self.assertNotContains(resposta, "<script>alert(1)</script>")
        self.assertContains(resposta, "&lt;script&gt;alert(1)&lt;/script&gt;")

    def test_quebras_de_linha_viram_paragrafos_no_detalhe(self):
        post = PostService.criar(self.autor, "Parágrafos", "Primeiro\n\nSegundo")
        PostService.publicar(post.pk, self.autor)

        resposta = self.client.get(reverse("posts:detalhe", args=[post.slug]))

        self.assertContains(resposta, "<p>Primeiro</p>", html=True)
        self.assertContains(resposta, "<p>Segundo</p>", html=True)


class AcessoAoPainelTests(PostViewTestCase):
    def _rotas_do_painel(self):
        id_do_post = self.rascunho.pk
        return [
            reverse("posts:painel"),
            reverse("posts:criar"),
            reverse("posts:editar", args=[id_do_post]),
            reverse("posts:excluir", args=[id_do_post]),
            reverse("posts:publicar", args=[id_do_post]),
            reverse("posts:despublicar", args=[id_do_post]),
        ]

    def test_visitante_e_redirecionado_para_o_login(self):
        entrar = reverse("contas:entrar")
        for url in self._rotas_do_painel():
            for metodo in (self.client.get, self.client.post):
                with self.subTest(url=url, metodo=metodo.__name__):
                    self.assertRedirects(metodo(url), f"{entrar}?next={url}")
        self.assertTrue(Post.objects.filter(pk=self.rascunho.pk).exists())

    def test_rotas_retornam_404_para_post_de_outro_autor(self):
        self.client.force_login(self.outro)
        id_do_post = self.rascunho.pk
        rotas = [
            ("get", "posts:editar"),
            ("post", "posts:editar"),
            ("get", "posts:excluir"),
            ("post", "posts:excluir"),
            ("post", "posts:publicar"),
            ("post", "posts:despublicar"),
        ]

        for metodo, nome in rotas:
            with self.subTest(metodo=metodo, rota=nome):
                resposta = getattr(self.client, metodo)(reverse(nome, args=[id_do_post]))
                self.assertEqual(resposta.status_code, 404)

        self.rascunho.refresh_from_db()
        self.assertEqual(self.rascunho.titulo, "Meu rascunho")
        self.assertEqual(self.rascunho.status, StatusPost.RASCUNHO)

    def test_get_em_publicar_e_despublicar_retorna_405(self):
        self.client.force_login(self.autor)

        for nome in ("posts:publicar", "posts:despublicar"):
            with self.subTest(rota=nome):
                resposta = self.client.get(reverse(nome, args=[self.rascunho.pk]))
                self.assertEqual(resposta.status_code, 405)


class PainelTests(PostViewTestCase):
    def setUp(self):
        self.client.force_login(self.autor)

    def test_painel_mostra_rascunhos_e_publicados_apenas_do_autor(self):
        PostService.criar(self.outro, "Post da outra", "C")

        resposta = self.client.get(reverse("posts:painel"))

        self.assertContains(resposta, "Meu rascunho")
        self.assertContains(resposta, "Meu publicado")
        self.assertNotContains(resposta, "Post da outra")

    def test_criar_grava_rascunho_do_usuario_logado(self):
        resposta = self.client.post(
            reverse("posts:criar"),
            {"titulo": "Novo post", "conteudo": "Texto", "status": "PUBLICADO"},
        )

        self.assertRedirects(resposta, reverse("posts:painel"))
        post = Post.objects.get(titulo="Novo post")
        self.assertEqual(post.autor, self.autor)
        self.assertEqual(post.status, StatusPost.RASCUNHO)

    def test_criar_com_dados_invalidos_mostra_erros_e_nao_grava(self):
        quantidade = Post.objects.count()

        resposta = self.client.post(reverse("posts:criar"), {"titulo": "", "conteudo": ""})

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["form"].errors)
        self.assertEqual(Post.objects.count(), quantidade)

    def test_editar_preenche_o_formulario(self):
        resposta = self.client.get(reverse("posts:editar", args=[self.rascunho.pk]))

        self.assertContains(resposta, "Meu rascunho")

    def test_editar_mantem_a_url_publica(self):
        url = reverse("posts:editar", args=[self.publicado.pk])

        resposta = self.client.post(url, {"titulo": "Título trocado", "conteudo": "Novo"})

        self.assertRedirects(resposta, reverse("posts:painel"))
        self.publicado.refresh_from_db()
        self.assertEqual(self.publicado.titulo, "Título trocado")
        self.assertEqual(self.publicado.slug, "meu-publicado")

    def test_editar_com_dados_invalidos_nao_grava(self):
        url = reverse("posts:editar", args=[self.rascunho.pk])

        resposta = self.client.post(url, {"titulo": "", "conteudo": "Novo"})

        self.assertEqual(resposta.status_code, 200)
        self.rascunho.refresh_from_db()
        self.assertEqual(self.rascunho.conteudo, "Texto do rascunho")

    def test_publicar_e_despublicar_alteram_o_status(self):
        url_publicar = reverse("posts:publicar", args=[self.rascunho.pk])
        url_despublicar = reverse("posts:despublicar", args=[self.rascunho.pk])

        self.assertRedirects(self.client.post(url_publicar), reverse("posts:painel"))
        self.rascunho.refresh_from_db()
        self.assertEqual(self.rascunho.status, StatusPost.PUBLICADO)

        self.assertRedirects(self.client.post(url_despublicar), reverse("posts:painel"))
        self.rascunho.refresh_from_db()
        self.assertEqual(self.rascunho.status, StatusPost.RASCUNHO)

    def test_get_em_excluir_pede_confirmacao_e_nao_exclui(self):
        resposta = self.client.get(reverse("posts:excluir", args=[self.rascunho.pk]))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "posts/confirmar_exclusao.html")
        self.assertTrue(Post.objects.filter(pk=self.rascunho.pk).exists())

    def test_post_em_excluir_exclui(self):
        resposta = self.client.post(reverse("posts:excluir", args=[self.rascunho.pk]))

        self.assertRedirects(resposta, reverse("posts:painel"))
        self.assertFalse(Post.objects.filter(pk=self.rascunho.pk).exists())
