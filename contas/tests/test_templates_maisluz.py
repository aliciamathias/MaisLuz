from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse


class TemplatesMaisLuzTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="cidadao_teste",
            cpf="123.456.789-00",
            email="cidadao@exemplo.com",
            password="senha-segura-123",
            nome_completo="Cidadão Teste",
            is_staff=False,
        )

    def test_rotas_cidadao_protegidas_redirecionam_quando_nao_logado(self):
        url_registrar = reverse('registrar_ocorrencia')
        url_minhas = reverse('minhas_ocorrencias')
        url_perfil = reverse('meu_perfil_cidadao')

        self.assertEqual(url_registrar, '/ocorrencias/registrar/')
        self.assertEqual(url_minhas, '/ocorrencias/minhas/')
        self.assertEqual(url_perfil, '/cidadao/perfil/')

        resp_reg = self.client.get(url_registrar)
        self.assertEqual(resp_reg.status_code, 302)
        self.assertIn(reverse('contas:entrar'), resp_reg.url)

        resp_min = self.client.get(url_minhas)
        self.assertEqual(resp_min.status_code, 302)
        self.assertIn(reverse('contas:entrar'), resp_min.url)

        resp_perfil = self.client.get(url_perfil)
        self.assertEqual(resp_perfil.status_code, 302)
        self.assertIn(reverse('contas:entrar'), resp_perfil.url)

    def test_rotas_cidadao_acessiveis_quando_logado(self):
        self.client.force_login(self.user)

        resp_reg = self.client.get(reverse('registrar_ocorrencia'))
        self.assertEqual(resp_reg.status_code, 200)
        self.assertContains(resp_reg, 'Vamos iluminar esse caminho?')

        resp_min = self.client.get(reverse('minhas_ocorrencias'))
        self.assertEqual(resp_min.status_code, 200)
        self.assertContains(resp_min, 'Suas solicitações em um só lugar')

        resp_perfil = self.client.get(reverse('meu_perfil_cidadao'))
        self.assertEqual(resp_perfil.status_code, 200)
        self.assertContains(resp_perfil, 'Dados do Cidadão')

    def test_landing_page_botao_registrar_problema_direciona_corretamente(self):
        # Deslogado: direciona para cadastro_cidadao
        resp_deslogado = self.client.get(reverse('inicio'))
        self.assertEqual(resp_deslogado.status_code, 200)
        self.assertContains(resp_deslogado, reverse('cadastro_cidadao'))

        # Logado como cidadão: direciona para registrar_ocorrencia
        self.client.force_login(self.user)
        resp_logado = self.client.get(reverse('inicio'))
        self.assertEqual(resp_logado.status_code, 200)
        self.assertContains(resp_logado, reverse('registrar_ocorrencia'))

    def test_rotas_publicas_e_internas_retornam_status_200(self):
        rotas = [
            (reverse('inicio'), 'Uma cidade mais iluminada e segura começa com você.'),
            (reverse('cadastro_cidadao'), 'Cadastro do cidadão'),
            (reverse('ocorrencias_painel'), 'Painel de gestão de ocorrências'),
            (reverse('cadastro_atendente'), 'Cadastro de atendente'),
            (reverse('editar_atendente'), 'Editar perfil de atendente'),
            (reverse('meu_perfil_interno'), 'Meu Perfil'),
            (reverse('recuperar_senha_cidadao'), 'Recuperar Senha'),
            (reverse('recuperar_senha_atendente'), 'Recuperar Senha'),
        ]

        for url, texto_esperado in rotas:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, texto_esperado)

    def test_sidebar_atendente_possui_apenas_ocorrencias_visao_geral_e_apoio(self):
        contexto = {
            'is_admin': False,
            'perfil': 'atendente',
        }
        html = render_to_string('partials/_sidebar_interno.html', contexto)

        self.assertIn('Visão geral', html)
        self.assertIn('Ocorrências', html)
        self.assertIn('Precisa de apoio?', html)
        self.assertIn('Área do Atendente', html)

        self.assertNotIn('<span>Funcionários</span>', html)
        self.assertNotIn('Listagem de funcionários', html)
        self.assertNotIn('Solicitações de Senha', html)
        self.assertNotIn('<span>Configurações</span>', html)

    def test_sidebar_administrador_possui_navbar_completa(self):
        contexto = {
            'is_admin': True,
            'perfil': 'administrador',
        }
        html = render_to_string('partials/_sidebar_interno.html', contexto)

        self.assertIn('Área do Administrador', html)
        self.assertIn('Visão geral', html)
        self.assertIn('Ocorrências', html)
        self.assertIn('<span>Funcionários</span>', html)
        self.assertIn('Listagem de funcionários', html)
        self.assertIn('Solicitações de Senha', html)
        self.assertIn('<span>Configurações</span>', html)
        self.assertIn('Precisa de apoio?', html)

    def test_header_e_footer_publico_renderizam_corretamente(self):
        header_html = render_to_string('partials/_header_publico.html', {})
        self.assertIn('MaisLuz', header_html)
        self.assertIn('Registrar ocorrência', header_html)
        self.assertIn('Minhas ocorrências', header_html)
        self.assertIn('Ajuda', header_html)

        footer_html = render_to_string('partials/_footer_publico.html', {})
        self.assertIn('Prefeitura Municipal de Maceió', footer_html)
        self.assertIn('Acessibilidade', footer_html)
        self.assertIn('Termos de uso', footer_html)
        self.assertIn('Atendimento 156', footer_html)

    def test_ocorrencias_atendente_carrega_css_e_elementos_acessiveis(self):
        contexto = {
            'is_admin': False,
            'perfil': 'atendente',
            'nav_ativa': 'ocorrencias',
        }
        html = render_to_string('ocorrencias/ocorrencias-atendente.html', contexto)

        self.assertIn('ocorrencias-atendente.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)
        self.assertIn('skip-link', html)
        self.assertIn('Pular para o conteúdo principal', html)
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('Painel de gestão de ocorrências', html)
        self.assertIn('Abertas', html)
        self.assertIn('Em Manutenção', html)
        self.assertIn('Concluídas', html)
        self.assertIn('ML-2026-0088', html)
        self.assertNotIn('tabindex="1"', html)
        self.assertNotIn('tabindex="2"', html)

    def test_cadastro_atendente_carrega_css_e_elementos_acessiveis(self):
        contexto = {
            'is_admin': True,
            'perfil': 'administrador',
            'nav_ativa': 'funcionarios',
        }
        html = render_to_string('funcionarios/cadastro-atendente.html', contexto)

        self.assertIn('cadastro-atendente.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('Cadastro de atendente', html)
        self.assertIn('id="id_cpf"', html)
        self.assertIn('for="id_cpf"', html)
        self.assertIn('id="id_nome"', html)
        self.assertIn('for="id_nome"', html)
        self.assertIn('id="id_celular"', html)
        self.assertIn('for="id_celular"', html)
        self.assertIn('id="id_email"', html)
        self.assertIn('for="id_email"', html)
        self.assertIn('modal-cancelar', html)
        self.assertNotIn('tabindex="1"', html)
        self.assertNotIn('tabindex="2"', html)

    def test_registrar_ocorrencia_cidadao_carrega_css_e_elementos_acessiveis(self):
        contexto = {}
        html = render_to_string('ocorrencias/registrar-ocorrencia-cidadao.html', contexto)

        self.assertIn('registrar-ocorrencia-cidadao.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('Vamos iluminar esse caminho?', html)
        self.assertIn('Qual é o problema?', html)
        self.assertIn('Onde está o poste?', html)
        self.assertIn('Adicione uma foto', html)
        self.assertIn('Fiação exposta ou risco imediato?', html)
        self.assertIn('Serviço gratuito', html)
        self.assertIn('id="id_logradouro"', html)
        self.assertIn('for="id_logradouro"', html)
        self.assertIn('id="id_rua"', html)
        self.assertIn('for="id_rua"', html)
        self.assertIn('id="id_bairro"', html)
        self.assertIn('for="id_bairro"', html)
        self.assertNotIn('tabindex="1"', html)
        self.assertNotIn('tabindex="2"', html)

    def test_landing_page_carrega_css_e_elementos_acessiveis(self):
        html = render_to_string('paginas/landing-page.html', {'header_variante': 'landing'})

        self.assertIn('landing-page.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('Como funciona o MaisLuz Maceió?', html)
        self.assertIn('Identifique o problema', html)
        self.assertIn('Abra o chamado em minutos', html)
        self.assertIn('Acompanhe a solução', html)
        self.assertNotIn('tabindex="1"', html)

    def test_cadastro_cidadao_carrega_css_e_elementos_acessiveis(self):
        html = render_to_string('cidadao/cadastro-cidadao.html', {'header_variante': 'cadastro'})

        self.assertIn('cadastro-cidadao.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('id="id_nome"', html)
        self.assertIn('for="id_nome"', html)
        self.assertIn('id="id_email"', html)
        self.assertIn('for="id_email"', html)
        self.assertIn('id="id_cep"', html)
        self.assertIn('for="id_cep"', html)
        self.assertIn('id="id_celular"', html)
        self.assertIn('for="id_celular"', html)
        self.assertIn('viacep.js', html)
        self.assertNotIn('tabindex="1"', html)

    def test_viacep_integrado_nos_tres_templates_do_cidadao(self):
        html_cadastro = render_to_string('cidadao/cadastro-cidadao.html', {'header_variante': 'cadastro'})
        self.assertIn('viacep.js', html_cadastro)
        self.assertIn('btn-buscar-cep', html_cadastro)
        self.assertIn('cep-feedback', html_cadastro)

        html_perfil = render_to_string('cidadao/meu-perfil-cidadao.html', {'usuario': self.user})
        self.assertIn('viacep.js', html_perfil)
        self.assertIn('btn-buscar-cep', html_perfil)
        self.assertIn('id="id_cep"', html_perfil)

        html_ocorrencia = render_to_string('ocorrencias/registrar-ocorrencia-cidadao.html', {})
        self.assertIn('viacep.js', html_ocorrencia)
        self.assertIn('id="id_cep_busca"', html_ocorrencia)
        self.assertIn('btn-buscar-cep', html_ocorrencia)
