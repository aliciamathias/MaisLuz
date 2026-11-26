from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from contas.forms import (
    CadastroCidadaoForm,
    EdicaoPerfilCidadaoForm,
    LoginForm,
)
from ocorrencias.forms import RegistroOcorrenciaForm
from ocorrencias.models import Ocorrencia


class FluxoCidadaoRequisitosTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = get_user_model().objects.create_user(
            username="cidadao1",
            cpf="111.222.333-44",
            email="cidadao1@exemplo.com",
            telefone="(82)99999-1111",
            password="senha-segura-123",
            nome_completo="Cidadão Um",
            is_staff=False,
        )

    # --- RF001: Validações e mensagens do Cadastro ---
    def test_rf001_nome_muito_curto(self):
        form = CadastroCidadaoForm(data={"nome": "Ab"})
        self.assertFalse(form.is_valid())
        self.assertIn("Nome muito curto", form.errors.get("nome", []))

    def test_rf001_cpf_quantidade_e_formato(self):
        form = CadastroCidadaoForm(data={"cpf": "123.456"})
        self.assertFalse(form.is_valid())
        self.assertIn("CPF não identificado", form.errors.get("cpf", []))

    def test_rf001_email_invalido(self):
        form = CadastroCidadaoForm(data={"email": "sem_arroba.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("Email inválido", form.errors.get("email", []))

    def test_rf001_telefone_invalido(self):
        form = CadastroCidadaoForm(data={"celular": "9999-1234"})
        self.assertFalse(form.is_valid())
        self.assertIn("Telefone inválido", form.errors.get("celular", []))

    def test_rf001_senha_curta(self):
        form = CadastroCidadaoForm(data={"senha": "123", "confirmacao_senha": "123"})
        self.assertFalse(form.is_valid())
        self.assertIn("A senha é muito curta", form.errors.get("senha", []))

    def test_rf001_senha_longa(self):
        senha_longa = "a" * 31
        form = CadastroCidadaoForm(data={"senha": senha_longa, "confirmacao_senha": senha_longa})
        self.assertFalse(form.is_valid())
        self.assertIn("A senha é muito longa", form.errors.get("senha", []))

    def test_rf001_senhas_diferentes(self):
        form = CadastroCidadaoForm(data={"senha": "senha-valida-1", "confirmacao_senha": "senha-valida-2"})
        self.assertFalse(form.is_valid())
        self.assertIn("As senhas são diferentes", form.errors.get("confirmacao_senha", []))

    def test_rf001_cep_curto_e_longo(self):
        form_curto = CadastroCidadaoForm(data={"cep": "1234"})
        self.assertFalse(form_curto.is_valid())
        self.assertIn("CEP muito curto", form_curto.errors.get("cep", []))

        form_longo = CadastroCidadaoForm(data={"cep": "12345-67890"})
        self.assertFalse(form_longo.is_valid())
        self.assertIn("CEP muito longo", form_longo.errors.get("cep", []))

    def test_rf001_campos_obrigatorios_nao_preenchidos(self):
        form = CadastroCidadaoForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("Campo(s) obrigatório(s) não preenchido(s)", form.errors.get("nome", []))

    def test_rf001_post_cadastro_sucesso_redireciona(self):
        dados = {
            "nome": "Cidadã Valéria Silva",
            "cpf": "999.888.777-66",
            "email": "valeria.silva@exemplo.com",
            "celular": "(82)98888-7777",
            "senha": "senha-forte-123",
            "confirmacao_senha": "senha-forte-123",
            "cep": "57035-160",
            "logradouro": "Avenida Fernandes Lima",
            "bairro": "Farol",
            "numero": "100",
            "complemento": "Apt 201",
        }
        resp = self.client.post(reverse("cadastro_cidadao"), dados)
        self.assertRedirects(resp, reverse("cadastro_sucesso"))
        self.assertTrue(get_user_model().objects.filter(cpf="999.888.777-66").exists())

    def test_rf001_post_cpf_duplicado(self):
        dados = {
            "nome": "Cidadã Outro Nome",
            "cpf": "111.222.333-44",
            "email": "novo.email@exemplo.com",
            "celular": "(82)98888-7777",
            "senha": "senha-forte-123",
            "confirmacao_senha": "senha-forte-123",
            "cep": "57035-160",
            "logradouro": "Avenida",
            "bairro": "Farol",
            "numero": "100",
        }
        resp = self.client.post(reverse("cadastro_cidadao"), dados)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "CPF já cadastrado")

    # --- RF002: Login e Autenticação do Cidadão ---
    def test_rf002_login_campos_obrigatorios(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("Campo(s) obrigatório(s) não preenchido(s)", form.errors.get("username", []))

    def test_rf002_login_credenciais_invalidas(self):
        resp = self.client.post(
            reverse("contas:entrar"),
            {"username": "111.222.333-44", "password": "senha-errada"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Usuário ou senha inválidos")

    def test_rf002_login_sucesso_com_cpf_redireciona_minhas_ocorrencias(self):
        resp = self.client.post(
            reverse("contas:entrar"),
            {"username": "111.222.333-44", "password": "senha-segura-123"},
        )
        self.assertRedirects(resp, reverse("minhas_ocorrencias"))

    def test_rf002_login_sucesso_com_email_redireciona_minhas_ocorrencias(self):
        resp = self.client.post(
            reverse("contas:entrar"),
            {"username": "cidadao1@exemplo.com", "password": "senha-segura-123"},
        )
        self.assertRedirects(resp, reverse("minhas_ocorrencias"))

    # --- RF005: Registro de Ocorrência ---
    def test_rf005_numero_poste_validacao(self):
        form_curto = RegistroOcorrenciaForm(data={"numero_poste": "123"})
        self.assertFalse(form_curto.is_valid())
        self.assertIn("Número de identificação do poste incorreta", form_curto.errors.get("numero_poste", []))

        form_longo = RegistroOcorrenciaForm(data={"numero_poste": "123456789012"})
        self.assertFalse(form_longo.is_valid())
        self.assertIn("Número de identificação do poste incorreta", form_longo.errors.get("numero_poste", []))

    def test_rf005_campos_obrigatorios(self):
        form = RegistroOcorrenciaForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("Campos obrigatórios não preenchidos", form.errors.get("logradouro", []))
        self.assertIn("Campos obrigatórios não preenchidos", form.errors.get("rua", []))
        self.assertIn("Campos obrigatórios não preenchidos", form.errors.get("bairro", []))
        self.assertIn("Campos obrigatórios não preenchidos", form.errors.get("ponto_referencia", []))

    def test_rf005_criar_ocorrencia_sucesso(self):
        self.client.force_login(self.usuario)
        dados = {
            "numero_poste": "04892188",
            "logradouro": "Avenida",
            "rua": "Sílvio Carlos Viana",
            "bairro": "Ponta Verde",
            "ponto_referencia": "Em frente ao quiosque 3",
            "tipo_problema": "Poste Apagado",
            "descricao": "Poste apagado à noite",
        }
        resp = self.client.post(reverse("registrar_ocorrencia"), dados, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Ocorrência registrada com sucesso! O chamado foi encaminhado para a empresa de energia.")
        self.assertTrue(Ocorrencia.objects.filter(numero_poste="04892188", cidadao=self.usuario).exists())

    # --- RF008: Edição de Perfil ---
    def test_rf008_edicao_perfil_sucesso(self):
        self.client.force_login(self.usuario)
        dados = {
            "nome": "Cidadão Um Atualizado",
            "email": "cidadao.novo@exemplo.com",
            "celular": "(82)98888-0000",
            "cep": "57035-160",
            "logradouro": "Rua Nova",
            "bairro": "Ponta Verde",
            "numero": "200",
            "complemento": "Apt 101",
        }
        resp = self.client.post(reverse("meu_perfil_cidadao"), dados, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Dados atualizados com sucesso")

        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome_completo, "Cidadão Um Atualizado")
        self.assertEqual(self.usuario.email, "cidadao.novo@exemplo.com")
        self.assertEqual(self.usuario.cpf, "111.222.333-44")  # CPF permanece imutável!

    def test_rf008_edicao_perfil_email_duplicado(self):
        outro_user = get_user_model().objects.create_user(
            username="cidadao2",
            cpf="222.333.444-55",
            email="outro@exemplo.com",
            password="senha-segura-123",
        )
        self.client.force_login(self.usuario)
        dados = {
            "nome": "Cidadão Um",
            "email": "outro@exemplo.com",
            "celular": "(82)98888-0000",
        }
        resp = self.client.post(reverse("meu_perfil_cidadao"), dados)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "E-mail já cadastrado")
