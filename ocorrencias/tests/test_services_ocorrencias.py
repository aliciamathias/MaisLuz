from django.contrib.auth import get_user_model
from django.test import TestCase
from contas.models import CargoFuncionario, TipoPerfil
from contas.services import CidadaoService
from ocorrencias.exceptions import (
    DadosInsuficientesErro,
    NumeroPosteInvalidoErro,
    OcorrenciaEmAndamentoErro,
    PermissaoOcorrenciaNegadaErro,
)
from ocorrencias.models import Ocorrencia, StatusOcorrencia, TipoDefeito
from ocorrencias.services import OcorrenciaService

Usuario = get_user_model()


class OcorrenciaServiceTests(TestCase):
    def setUp(self):
        self.cidadao = CidadaoService.cadastrar(
            nome_completo="Carlos Cidadão Exemplo",
            cpf="555.666.777-88",
            email="carlos.exemplo@teste.com",
            telefone="(82)98844-5566",
            senha="senhaExemplo123",
            confirmacao_senha="senhaExemplo123",
            cep="57000-000",
            logradouro="Avenida da Paz",
            bairro="Centro",
            numero="500",
        )
        self.gestor = Usuario.objects.create_user(
            username="gestor1",
            nome_completo="Gestor Operacional",
            cpf="666.777.888-99",
            matricula_funcional="1010",
            cargo=CargoFuncionario.GESTOR_SISTEMA,
            tipo_perfil=TipoPerfil.FUNCIONARIO,
            is_staff=True,
        )

    def test_criacao_ocorrencia_com_sucesso(self):
        ocorrencia = OcorrenciaService.criar_ocorrencia(
            cidadao=self.cidadao,
            numero_poste="12345678",
            logradouro="Avenida da Paz",
            rua="Rua da Praia",
            bairro="Centro",
            ponto_referencia="Em frente à praça",
            tipo_defeito=TipoDefeito.POSTE_APAGADO,
            descricao="Lâmpada apagada há 3 dias",
        )
        self.assertEqual(len(ocorrencia.protocolo), 10)
        self.assertEqual(ocorrencia.status, StatusOcorrencia.PENDENTE)
        self.assertEqual(ocorrencia.cpf_cidadao_snapshot, self.cidadao.cpf)

        # Verifica Foreign Key no HistoricoAuditoria
        auditoria = ocorrencia.historicos_auditoria.first()
        self.assertIsNotNone(auditoria)
        self.assertEqual(auditoria.ocorrencia, ocorrencia)
        self.assertEqual(auditoria.protocolo_ocorrencia, ocorrencia.protocolo)

    def test_validacao_tamanho_numero_poste(self):
        with self.assertRaises(NumeroPosteInvalidoErro):
            OcorrenciaService.criar_ocorrencia(
                cidadao=self.cidadao,
                numero_poste="1234",  # < 8
                logradouro="Avenida da Paz",
                rua="Rua da Praia",
                bairro="Centro",
                ponto_referencia="Em frente à praça",
                tipo_defeito=TipoDefeito.POSTE_APAGADO,
            )

        with self.assertRaises(NumeroPosteInvalidoErro):
            OcorrenciaService.criar_ocorrencia(
                cidadao=self.cidadao,
                numero_poste="12345678901",  # > 10
                logradouro="Avenida da Paz",
                rua="Rua da Praia",
                bairro="Centro",
                ponto_referencia="Em frente à praça",
                tipo_defeito=TipoDefeito.POSTE_APAGADO,
            )

    def test_exclusao_logica_cidadao_apenas_quando_pendente(self):
        ocorrencia = OcorrenciaService.criar_ocorrencia(
            cidadao=self.cidadao,
            numero_poste="88776655",
            logradouro="Avenida da Paz",
            rua="Rua da Praia",
            bairro="Centro",
            ponto_referencia="Em frente à praça",
            tipo_defeito=TipoDefeito.POSTE_APAGADO,
        )

        # Pendente -> sucesso na exclusão lógica pelo cidadão
        OcorrenciaService.excluir_logica_cidadao(ocorrencia, self.cidadao)
        ocorrencia.refresh_from_db()
        self.assertEqual(ocorrencia.status, StatusOcorrencia.EXCLUIDO_CIDADAO)

        # Em progresso -> não permite exclusão pelo cidadão
        ocorrencia.status = StatusOcorrencia.EM_PROGRESSO
        ocorrencia.save()

        with self.assertRaises(OcorrenciaEmAndamentoErro):
            OcorrenciaService.excluir_logica_cidadao(ocorrencia, self.cidadao)

    def test_exclusao_logica_funcionario(self):
        ocorrencia = OcorrenciaService.criar_ocorrencia(
            cidadao=self.cidadao,
            numero_poste="88776655",
            logradouro="Avenida da Paz",
            rua="Rua da Praia",
            bairro="Centro",
            ponto_referencia="Em frente à praça",
            tipo_defeito=TipoDefeito.POSTE_APAGADO,
        )

        OcorrenciaService.excluir_logica_funcionario(
            ocorrencia, self.gestor, justificativa="Duplicidade identificada"
        )
        ocorrencia.refresh_from_db()
        self.assertEqual(ocorrencia.status, StatusOcorrencia.EXCLUIDO_FUNCIONARIO)
        self.assertEqual(ocorrencia.atendente, self.gestor)
        auditoria = ocorrencia.historicos_auditoria.filter(tipo_operacao='EXCLUSAO_OCORRENCIA_FUNCIONARIO').first()
        self.assertIsNotNone(auditoria)
        self.assertEqual(auditoria.ocorrencia, ocorrencia)
