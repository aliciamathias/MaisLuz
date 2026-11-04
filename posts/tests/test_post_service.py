from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from posts.exceptions import PostNaoEncontrado
from posts.models import Comentario, Post, StatusPost
from posts.services import PostService


class PostServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuarios = get_user_model().objects
        cls.autor = usuarios.create_user("autora")
        cls.outro = usuarios.create_user("outra")

    def _publicado(self, titulo="Publicado", autor=None):
        post = PostService.criar(autor or self.autor, titulo, "Conteúdo")
        return PostService.publicar(post.pk, autor or self.autor)


class CriarTests(PostServiceTestCase):
    def test_gera_rascunho_com_slug_de_titulo_acentuado(self):
        post = PostService.criar(self.autor, "Olá, Coração!", "Conteúdo")

        self.assertEqual(post.status, StatusPost.RASCUNHO)
        self.assertIsNone(post.publicado_em)
        self.assertEqual(post.slug, "ola-coracao")

    def test_titulos_iguais_geram_slugs_diferentes(self):
        slugs = [PostService.criar(self.autor, "Mesmo título", "C").slug for _ in range(3)]

        self.assertEqual(slugs, ["mesmo-titulo", "mesmo-titulo-2", "mesmo-titulo-3"])

    def test_titulo_sem_caracteres_validos_usa_base_post(self):
        primeiro = PostService.criar(self.autor, "!!!", "C")
        segundo = PostService.criar(self.autor, "???", "C")

        self.assertEqual(primeiro.slug, "post")
        self.assertEqual(segundo.slug, "post-2")

    def test_base_do_slug_tem_no_maximo_200_caracteres(self):
        post = PostService.criar(self.autor, "a" * 200 + "b", "C")

        self.assertEqual(post.slug, "a" * 200)

    def test_corte_do_slug_nao_deixa_hifen_no_fim(self):
        titulo = "a" * 199 + " bcd"

        primeiro = PostService.criar(self.autor, titulo, "C")
        segundo = PostService.criar(self.autor, titulo, "C")

        self.assertEqual(primeiro.slug, "a" * 199)
        self.assertEqual(segundo.slug, "a" * 199 + "-2")


class AtualizarTests(PostServiceTestCase):
    def test_nao_altera_slug_status_nem_data(self):
        post = self._publicado("Título original")
        data = post.publicado_em

        PostService.atualizar(post.pk, self.autor, "Título novo", "Novo conteúdo")

        post.refresh_from_db()
        self.assertEqual(post.titulo, "Título novo")
        self.assertEqual(post.conteudo, "Novo conteúdo")
        self.assertEqual(post.slug, "titulo-original")
        self.assertEqual(post.status, StatusPost.PUBLICADO)
        self.assertEqual(post.publicado_em, data)


class PublicacaoTests(PostServiceTestCase):
    def test_publicar_preenche_data_na_primeira_vez(self):
        post = PostService.criar(self.autor, "Título", "C")

        post = PostService.publicar(post.pk, self.autor)

        self.assertEqual(post.status, StatusPost.PUBLICADO)
        self.assertIsNotNone(post.publicado_em)

    def test_publicar_de_novo_nao_altera_nada(self):
        post = self._publicado()
        data, atualizado_em = post.publicado_em, post.atualizado_em

        PostService.publicar(post.pk, self.autor)

        post.refresh_from_db()
        self.assertEqual(post.publicado_em, data)
        self.assertEqual(post.atualizado_em, atualizado_em)

    def test_despublicar_volta_para_rascunho_e_sai_da_listagem(self):
        post = self._publicado()
        data = post.publicado_em

        PostService.despublicar(post.pk, self.autor)

        post.refresh_from_db()
        self.assertEqual(post.status, StatusPost.RASCUNHO)
        self.assertEqual(post.publicado_em, data)
        self.assertEqual(list(PostService.listar_publicados()), [])

    def test_republicar_mantem_a_data_original(self):
        post = self._publicado()
        data = post.publicado_em
        PostService.despublicar(post.pk, self.autor)

        post = PostService.publicar(post.pk, self.autor)

        self.assertEqual(post.publicado_em, data)

    def test_banco_rejeita_publicado_sem_data(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Post.objects.create(
                autor=self.autor,
                titulo="T",
                slug="t",
                conteudo="C",
                status=StatusPost.PUBLICADO,
            )


class ExcluirTests(PostServiceTestCase):
    def test_excluir_remove_o_post_e_seus_comentarios(self):
        post = self._publicado()
        Comentario.objects.create(post=post, nome="Ana", texto="Oi")

        PostService.excluir(post.pk, self.autor)

        self.assertFalse(Post.objects.exists())
        self.assertFalse(Comentario.objects.exists())


class PosseTests(PostServiceTestCase):
    def test_operacoes_com_post_de_outro_autor_levantam_excecao(self):
        post = self._publicado()
        operacoes = {
            "obter_do_autor": lambda: PostService.obter_do_autor(post.pk, self.outro),
            "atualizar": lambda: PostService.atualizar(post.pk, self.outro, "T", "C"),
            "publicar": lambda: PostService.publicar(post.pk, self.outro),
            "despublicar": lambda: PostService.despublicar(post.pk, self.outro),
            "excluir": lambda: PostService.excluir(post.pk, self.outro),
        }

        for nome, operacao in operacoes.items():
            with self.subTest(operacao=nome), self.assertRaises(PostNaoEncontrado):
                operacao()

        post.refresh_from_db()
        self.assertEqual(post.titulo, "Publicado")
        self.assertEqual(post.status, StatusPost.PUBLICADO)

    def test_obter_publicado_levanta_excecao_para_rascunho_e_slug_inexistente(self):
        rascunho = PostService.criar(self.autor, "Rascunho", "C")

        for slug in (rascunho.slug, "nao-existe"):
            with self.subTest(slug=slug), self.assertRaises(PostNaoEncontrado):
                PostService.obter_publicado(slug)


class ListagemTests(PostServiceTestCase):
    def test_listar_publicados_ignora_rascunhos(self):
        publicado = self._publicado()
        PostService.criar(self.autor, "Rascunho", "C")

        self.assertEqual(list(PostService.listar_publicados()), [publicado])

    def test_listar_publicados_ordena_do_mais_recente_para_o_mais_antigo(self):
        antigo = self._publicado("Antigo")
        recente = self._publicado("Recente")
        Post.objects.filter(pk=antigo.pk).update(publicado_em=timezone.now() - timedelta(days=2))

        self.assertEqual(list(PostService.listar_publicados()), [recente, antigo])

    def test_listar_publicados_pagina_de_10_em_10(self):
        for indice in range(11):
            self._publicado(f"Post {indice}")

        primeira = PostService.listar_publicados()
        segunda = PostService.listar_publicados(2)

        self.assertEqual(len(primeira), 10)
        self.assertEqual(len(segunda), 1)

    def test_pagina_invalida_segue_get_page(self):
        for indice in range(11):
            self._publicado(f"Post {indice}")

        self.assertEqual(PostService.listar_publicados("abc").number, 1)
        self.assertEqual(PostService.listar_publicados(99).number, 2)

    def test_listar_publicados_nao_faz_consulta_extra_por_autor(self):
        self._publicado("Um")
        self._publicado("Dois", autor=self.outro)

        # Uma consulta para o total da paginação e outra para os posts com o autor.
        with self.assertNumQueries(2):
            [post.autor.username for post in PostService.listar_publicados()]

    def test_listar_do_autor_inclui_rascunhos_e_ignora_outros_autores(self):
        primeiro = PostService.criar(self.autor, "Primeiro", "C")
        segundo = self._publicado("Segundo")
        Post.objects.filter(pk=primeiro.pk).update(criado_em=timezone.now() - timedelta(days=1))
        self._publicado("De outra", autor=self.outro)

        self.assertEqual(list(PostService.listar_do_autor(self.autor)), [segundo, primeiro])

    def test_listar_do_autor_pagina_de_10_em_10(self):
        for indice in range(11):
            PostService.criar(self.autor, f"Post {indice}", "C")

        self.assertEqual(len(PostService.listar_do_autor(self.autor)), 10)
        self.assertEqual(len(PostService.listar_do_autor(self.autor, 2)), 1)
