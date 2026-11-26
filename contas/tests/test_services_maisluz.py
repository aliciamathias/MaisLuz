from django.contrib.auth import get_user_model
from django.test import TestCase
from contas.exceptions import (
    CampoImutavelErro,
    CampoObrigatorioErro,
    CPFCadastradoErro,
    CPFInvalidoErro,
    CredenciaisRecuperacaoInvalidasErro,
    JustificativaObrigatoriaErro,
    NomeCurtoErro,
    PermissaoNegadaErro,
    SenhaCurtaErro,
    SenhaLongaErro,
    SenhasDiferentesErro,
    TelefoneInvalidoErro,
)
from contas.models import (
    CargoFuncionario,
    HistoricoAuditoria,
    SolicitacaoRecuperacaoSenha,
    StatusAcesso,
    StatusSolicitacao,
    TipoOperacaoAuditoria,
    TipoPerfil,
)
from contas.services import (
    BloqueioService,
    CidadaoService,
    FuncionarioService,
    RecuperacaoSenhaService,
)

Usuario = get_user_model()


class CidadaoServiceTests(TestCase):
    def test_cadastro_cidadao_com_sucesso(self):
        usuario = CidadaoService.cadastrar(
            nome_completo="Maria Silva Santos",
            cpf="123.456.789-00",
            email="maria@exemplo.com",
            telefone="(82)98877-6655",
            senha="senhaSegura123",
            confirmacao_senha="senhaSegura123",
            cep="57000-000",
            logradouro="Rua das Flores",
            bairro="Centro",
            numero="100",
            complemento="Apto 101",
        )
        self.assertEqual(usuario.tipo_perfil, TipoPerfil.CIDADAO)
        self.assertEqual(usuario.cpf, "123.456.789-00")
        self.assertEqual(usuario.telefone, "(82)98877-6655")
        self.assertTrue(usuario.check_password("senhaSegura123"))
        self.assertTrue(
            HistoricoAuditoria.objects.filter(
                usuario_afetado=usuario,
                tipo_operacao=TipoOperacaoAuditoria.CADASTRO_CIDADAO,
            ).exists()
        )

    def test_validacao_cpf_invalido(self):
        with self.assertRaises(CPFInvalidoErro):
            CidadaoService.cadastrar(
                nome_completo="Maria Silva Santos",
                cpf="123.456",
                email="maria@exemplo.com",
                telefone="(82)98877-6655",
                senha="senhaSegura123",
                confirmacao_senha="senhaSegura123",
                cep="57000-000",
                logradouro="Rua das Flores",
                bairro="Centro",
                numero="100",
            )

    def test_validacao_nome_muito_curto(self):
        with self.assertRaises(NomeCurtoErro):
            CidadaoService.cadastrar(
                nome_completo="Zé",
                cpf="123.456.789-00",
                email="maria@exemplo.com",
                telefone="(82)98877-6655",
                senha="senhaSegura123",
                confirmacao_senha="senhaSegura123",
                cep="57000-000",
                logradouro="Rua das Flores",
                bairro="Centro",
                numero="100",
            )

    def test_validacao_senha_curta_e_longa_e_diferente(self):
        with self.assertRaises(SenhaCurtaErro):
            CidadaoService.cadastrar(
                nome_completo="Maria Silva Santos",
                cpf="123.456.789-00",
                email="maria@exemplo.com",
                telefone="(82)98877-6655",
                senha="curta",
                confirmacao_senha="curta",
                cep="57000-000",
                logradouro="Rua das Flores",
                bairro="Centro",
                numero="100",
            )

        with self.assertRaises(SenhaLongaErro):
            CidadaoService.cadastrar(
                nome_completo="Maria Silva Santos",
                cpf="123.456.789-00",
                email="maria@exemplo.com",
                telefone="(82)98877-6655",
                senha="a" * 31,
                confirmacao_senha="a" * 31,
                cep="57000-000",
                logradouro="Rua das Flores",
                bairro="Centro",
                numero="100",
            )

        with self.assertRaises(SenhasDiferentesErro):
            CidadaoService.cadastrar(
                nome_completo="Maria Silva Santos",
                cpf="123.456.789-00",
                email="maria@exemplo.com",
                telefone="(82)98877-6655",
                senha="senhaValida123",
                confirmacao_senha="senhaDiferente123",
                cep="57000-000",
                logradouro="Rua das Flores",
                bairro="Centro",
                numero="100",
            )

    def test_cpf_e_imutavel_na_edicao(self):
        usuario = CidadaoService.cadastrar(
            nome_completo="Maria Silva Santos",
            cpf="123.456.789-00",
            email="maria@exemplo.com",
            telefone="(82)98877-6655",
            senha="senhaSegura123",
            confirmacao_senha="senhaSegura123",
            cep="57000-000",
            logradouro="Rua das Flores",
            bairro="Centro",
            numero="100",
        )
        with self.assertRaises(CampoImutavelErro):
            CidadaoService.editar_perfil(
                usuario=usuario,
                operador=usuario,
                cpf="999.888.777-66",
            )

    def test_exclusao_logica_com_anonimizacao(self):
        usuario = CidadaoService.cadastrar(
            nome_completo="Maria Silva Santos",
            cpf="123.456.789-00",
            email="maria@exemplo.com",
            telefone="(82)98877-6655",
            senha="senhaSegura123",
            confirmacao_senha="senhaSegura123",
            cep="57000-000",
            logradouro="Rua das Flores",
            bairro="Centro",
            numero="100",
        )
        CidadaoService.anonimizar(usuario, operador=usuario)
        usuario.refresh_from_db()
        self.assertTrue(usuario.anonimizado)
        self.assertFalse(usuario.is_active)
        self.assertEqual(usuario.status_acesso, StatusAcesso.INATIVO)
        self.assertEqual(usuario.nome_completo, "Cidadão Anonimizado")
        self.assertIsNone(usuario.cpf)


class FuncionarioServiceTests(TestCase):
    def test_cadastro_funcionario_e_bloqueio_de_alteracao_de_matricula_e_cpf(self):
        admin = Usuario.objects.create_superuser("admin", "admin@teste.com", "senha123")
        admin.cargo = CargoFuncionario.ADMINISTRADOR
        admin.tipo_perfil = TipoPerfil.FUNCIONARIO
        admin.save()

        func = FuncionarioService.cadastrar(
            nome_completo="Carlos Atendente",
            cpf="111.222.333-44",
            matricula_funcional="8842",
            cargo=CargoFuncionario.ATENDENTE,
            email="carlos@empresa.com",
            telefone="(82)98811-2233",
            senha="senhaAtendente123",
            confirmacao_senha="senhaAtendente123",
            operador=admin,
        )
        self.assertEqual(func.matricula_funcional, "8842")
        self.assertEqual(func.tipo_perfil, TipoPerfil.FUNCIONARIO)

        with self.assertRaises(CampoImutavelErro):
            FuncionarioService.editar_perfil(
                usuario=func,
                operador=admin,
                matricula_funcional="9999",
            )

        with self.assertRaises(CampoImutavelErro):
            FuncionarioService.editar_perfil(
                usuario=func,
                operador=admin,
                cpf="999.999.999-99",
            )


class RecuperacaoSenhaServiceTests(TestCase):
    def test_fluxo_diferenciado_cidadao_vs_funcionario(self):
        cidadao = CidadaoService.cadastrar(
            nome_completo="João Cidadão",
            cpf="222.333.444-55",
            email="joao@teste.com",
            telefone="(82)99911-2233",
            senha="senhaCidadao1",
            confirmacao_senha="senhaCidadao1",
            cep="57000-000",
            logradouro="Rua A",
            bairro="Farol",
            numero="10",
        )
        func = FuncionarioService.cadastrar(
            nome_completo="Roberta Gestora",
            cpf="333.444.555-66",
            matricula_funcional="7711",
            cargo=CargoFuncionario.GESTOR_SISTEMA,
            email="roberta@empresa.com",
            telefone="(82)99922-3344",
            senha="senhaGestora1",
            confirmacao_senha="senhaGestora1",
        )

        # Cidadão: redefinição direta
        res_cid = RecuperacaoSenhaService.solicitar_recuperacao(
            "222.333.444-55", "(82)99911-2233"
        )
        self.assertEqual(res_cid["tipo"], "CIDADAO")

        RecuperacaoSenhaService.redefinir_senha_cidadao(
            cidadao, "novaSenhaSegura1", "novaSenhaSegura1"
        )
        cidadao.refresh_from_db()
        self.assertTrue(cidadao.check_password("novaSenhaSegura1"))

        # Funcionário: cria solicitação pendente para aprovação do administrador
        res_func = RecuperacaoSenhaService.solicitar_recuperacao(
            "333.444.555-66", "(82)99922-3344"
        )
        self.assertEqual(res_func["tipo"], "FUNCIONARIO")
        self.assertIn("autorização do Administrador", res_func["mensagem"])

        solicitacao = SolicitacaoRecuperacaoSenha.objects.filter(funcionario=func).first()
        self.assertIsNotNone(solicitacao)
        self.assertEqual(solicitacao.status, StatusSolicitacao.PENDENTE)


class BloqueioServiceTests(TestCase):
    def test_bloqueio_e_desbloqueio_por_administrador_com_justificativa(self):
        admin = Usuario.objects.create_superuser("admin_bloq", "admin@teste.com", "senha123")
        admin.cargo = CargoFuncionario.ADMINISTRADOR
        admin.tipo_perfil = TipoPerfil.FUNCIONARIO
        admin.save()

        alvo = CidadaoService.cadastrar(
            nome_completo="Usuário Suspeito",
            cpf="444.555.666-77",
            email="suspeito@teste.com",
            telefone="(82)99933-4455",
            senha="senhaSuspeita1",
            confirmacao_senha="senhaSuspeita1",
            cep="57000-000",
            logradouro="Rua B",
            bairro="Pajuçara",
            numero="20",
        )

        with self.assertRaises(JustificativaObrigatoriaErro):
            BloqueioService.bloquear_usuario(alvo, admin, justificativa="")

        BloqueioService.bloquear_usuario(
            alvo, admin, justificativa="Envio reiterado de trotes"
        )
        alvo.refresh_from_db()
        self.assertEqual(alvo.status_acesso, StatusAcesso.BLOQUEADO)
        self.assertFalse(alvo.is_active)

        # Desbloqueio
        BloqueioService.desbloquear_usuario(
            alvo, admin, justificativa="Esclarecimento prestado e advertência aceita"
        )
        alvo.refresh_from_db()
        self.assertEqual(alvo.status_acesso, StatusAcesso.ATIVO)
        self.assertTrue(alvo.is_active)
