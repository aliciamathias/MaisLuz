from django.template.loader import render_to_string
from django.test import Client, RequestFactory, SimpleTestCase
from django.urls import reverse


class TemplatesMaisLuzTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.client = Client()

    def test_rotas_das_novas_telas_retornam_status_200(self):
        url_ocorrencias = reverse('ocorrencias_painel')
        url_cadastro = reverse('cadastro_atendente')
        url_registrar = reverse('registrar_ocorrencia')

        self.assertEqual(url_ocorrencias, '/ocorrencias/painel/')
        self.assertEqual(url_cadastro, '/funcionarios/cadastro/')
        self.assertEqual(url_registrar, '/ocorrencias/registrar/')

        resposta_ocorrencias = self.client.get(url_ocorrencias)
        self.assertEqual(resposta_ocorrencias.status_code, 200)
        self.assertContains(resposta_ocorrencias, 'Painel de gestão de ocorrências')

        resposta_cadastro = self.client.get(url_cadastro)
        self.assertEqual(resposta_cadastro.status_code, 200)
        self.assertContains(resposta_cadastro, 'Cadastro de atendente')

        resposta_registrar = self.client.get(url_registrar)
        self.assertEqual(resposta_registrar.status_code, 200)
        self.assertContains(resposta_registrar, 'Vamos iluminar esse caminho?')

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

        # Regra explícita: Atendente NÃO tem Funcionários nem Configurações
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
        self.assertIn('Ana • Cidadã', header_html)

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

        # Mapeamento 1:1 CSS
        self.assertIn('ocorrencias-atendente.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)

        # Skip link WCAG AA
        self.assertIn('skip-link', html)
        self.assertIn('Pular para o conteúdo principal', html)

        # Título principal h1 e seções
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('Painel de gestão de ocorrências', html)
        self.assertIn('Abertas', html)
        self.assertIn('Em Manutenção', html)
        self.assertIn('Concluídas', html)
        self.assertIn('ML-2026-0088', html)

        # Não pode conter tabindex positivo
        self.assertNotIn('tabindex="1"', html)
        self.assertNotIn('tabindex="2"', html)

    def test_cadastro_atendente_carrega_css_e_elementos_acessiveis(self):
        contexto = {
            'is_admin': True,
            'perfil': 'administrador',
            'nav_ativa': 'funcionarios',
        }
        html = render_to_string('funcionarios/cadastro-atendente.html', contexto)

        # Mapeamento 1:1 CSS
        self.assertIn('cadastro-atendente.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)

        # Título principal h1 e formulário
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

        # Não pode conter tabindex positivo
        self.assertNotIn('tabindex="1"', html)
        self.assertNotIn('tabindex="2"', html)

    def test_registrar_ocorrencia_cidadao_carrega_css_e_elementos_acessiveis(self):
        contexto = {}
        html = render_to_string('ocorrencias/registrar-ocorrencia-cidadao.html', contexto)

        # Mapeamento 1:1 CSS
        self.assertIn('registrar-ocorrencia-cidadao.css', html)
        self.assertIn('root.css', html)
        self.assertIn('partials.css', html)

        # Título principal h1 e etapas
        self.assertEqual(html.count('<h1'), 1)
        self.assertIn('Vamos iluminar esse caminho?', html)
        self.assertIn('Qual é o problema?', html)
        self.assertIn('Onde está o poste?', html)
        self.assertIn('Adicione uma foto', html)
        self.assertIn('Fiação exposta ou risco imediato?', html)
        self.assertIn('Serviço gratuito', html)

        # Inputs com labels associados
        self.assertIn('id="id_logradouro"', html)
        self.assertIn('for="id_logradouro"', html)
        self.assertIn('id="id_rua"', html)
        self.assertIn('for="id_rua"', html)
        self.assertIn('id="id_bairro"', html)
        self.assertIn('for="id_bairro"', html)

        # Não pode conter tabindex positivo
        self.assertNotIn('tabindex="1"', html)
        self.assertNotIn('tabindex="2"', html)
