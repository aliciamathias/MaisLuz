from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from contas.models import TipoPerfil

SENHA = "senha-de-teste-123"


class EntrarViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("contas:entrar")
        cls.autor = get_user_model().objects.create_user(
            "autora",
            password=SENHA,
            is_staff=True,
            tipo_perfil=TipoPerfil.FUNCIONARIO,
        )
        cls.cidadao = get_user_model().objects.create_user(
            "cidadao",
            password=SENHA,
            is_staff=False,
            tipo_perfil=TipoPerfil.CIDADAO,
        )

    def _entrar(self, senha=SENHA, usuario="autora", **extra):
        return self.client.post(self.url, {"username": usuario, "password": senha, **extra})

    def test_get_exibe_formulario_com_csrf(self):
        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "csrfmiddlewaretoken")

    def test_credenciais_validas_redirecionam_para_o_painel_se_funcionario(self):
        resposta = self._entrar(usuario="autora")

        self.assertRedirects(resposta, reverse("ocorrencias_painel"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_credenciais_validas_redirecionam_para_minhas_ocorrencias_se_cidadao(self):
        resposta = self._entrar(usuario="cidadao")

        self.assertRedirects(resposta, reverse("minhas_ocorrencias"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_senha_errada_nao_cria_sessao_e_mostra_erro(self):
        resposta = self._entrar(senha="errada")

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(resposta.context["form"].non_field_errors())

    def test_erro_nao_revela_se_o_usuario_existe(self):
        senha_errada = self._entrar(senha="errada")
        usuario_inexistente = self._entrar(usuario="ninguem", senha="errada")

        self.assertEqual(
            senha_errada.context["form"].non_field_errors(),
            usuario_inexistente.context["form"].non_field_errors(),
        )

    def test_conta_inativa_nao_entra(self):
        get_user_model().objects.create_user(
            "inativa",
            password=SENHA,
            is_active=False,
            tipo_perfil=TipoPerfil.FUNCIONARIO,
        )

        resposta = self._entrar(usuario="inativa")

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_next_interno_e_respeitado(self):
        destino = reverse("cadastro_atendente")

        resposta = self._entrar(next=destino)

        self.assertRedirects(resposta, destino)

    def test_next_externo_e_ignorado(self):
        resposta = self._entrar(next="https://exemplo.com")

        self.assertRedirects(resposta, reverse("ocorrencias_painel"))

    def test_next_sem_barra_nao_e_tratado_como_nome_de_rota(self):
        resposta = self._entrar(next="sem-barra")

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, "sem-barra")

    def test_get_repassa_next_interno_em_campo_oculto(self):
        resposta = self.client.get(self.url, {"next": "/ocorrencias/painel/"})

        self.assertContains(resposta, '<input type="hidden" name="next" value="/ocorrencias/painel/">', html=True)

    def test_get_descarta_next_externo(self):
        resposta = self.client.get(self.url, {"next": "https://exemplo.com"})

        self.assertNotContains(resposta, "exemplo.com")

    def test_post_invalido_mantem_next_no_formulario(self):
        resposta = self._entrar(senha="errada", next="/ocorrencias/painel/")

        self.assertContains(resposta, '<input type="hidden" name="next" value="/ocorrencias/painel/">', html=True)

    def test_usuario_autenticado_e_redirecionado_para_o_painel(self):
        self.client.force_login(self.autor)

        resposta = self.client.get(self.url)

        self.assertRedirects(resposta, reverse("ocorrencias_painel"))


class SairViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("contas:sair")
        cls.autor = get_user_model().objects.create_user("autora", password=SENHA)

    def test_post_encerra_a_sessao(self):
        self.client.force_login(self.autor)

        resposta = self.client.post(self.url)

        self.assertRedirects(resposta, reverse("inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_retorna_405_e_mantem_a_sessao(self):
        self.client.force_login(self.autor)

        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_visitante_e_redirecionado_para_o_login(self):
        resposta = self.client.post(self.url)

        self.assertRedirects(resposta, f"{reverse('contas:entrar')}?next={self.url}")


class LayoutBaseTests(TestCase):
    def test_html_declara_idioma_e_viewport(self):
        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, '<html lang="pt-br">')
        self.assertContains(resposta, 'name="viewport"')
