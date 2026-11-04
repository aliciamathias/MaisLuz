from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse

from posts.models import Post, StatusPost
from posts.publicacoes_iniciais import PUBLICACOES_INICIAIS


class CriarPublicacoesIniciaisTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.autor = get_user_model().objects.create_user("autora", password="senha-de-teste")

    def _executar(self, autor: str = "autora") -> None:
        call_command("criar_publicacoes_iniciais", autor=autor, stdout=StringIO())

    def test_cria_todas_publicadas_para_o_autor_informado(self):
        self._executar()

        posts = Post.objects.filter(autor=self.autor, status=StatusPost.PUBLICADO)
        self.assertEqual(posts.count(), len(PUBLICACOES_INICIAIS))
        self.assertFalse(posts.filter(publicado_em__isnull=True).exists())

    def test_executar_de_novo_nao_duplica(self):
        self._executar()
        self._executar()

        self.assertEqual(Post.objects.count(), len(PUBLICACOES_INICIAIS))

    def test_autor_inexistente_gera_erro_sem_criar_posts(self):
        with self.assertRaises(CommandError):
            self._executar(autor="ninguem")

        self.assertFalse(Post.objects.exists())

    def test_boas_vindas_aparece_primeiro_na_pagina_inicial(self):
        self._executar()

        resposta = self.client.get(reverse("posts:lista"))

        self.assertEqual(resposta.context["posts"][0].titulo, PUBLICACOES_INICIAIS[-1]["titulo"])
