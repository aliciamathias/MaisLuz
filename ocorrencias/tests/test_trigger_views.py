from django.db import connection
from django.test import TestCase
from contas.models import Usuario, TipoPerfil
from ocorrencias.models import Ocorrencia, StatusOcorrencia, TipoDefeito


class TriggerEViewsTestCase(TestCase):
    def setUp(self):
        self.cidadao = Usuario.objects.create_user(
            username='cidadao_teste_trg',
            cpf='11122233344',
            nome_completo='Cidadão Teste Trigger',
            email='cidadao_trg@teste.com',
            tipo_perfil=TipoPerfil.CIDADAO,
        )

    def test_trigger_historico_ocorrencias_salva_apenas_em_mudanca_de_status(self):
        ocorrencia = Ocorrencia.objects.create(
            protocolo='TRG111111',
            numero_poste='PST1111',
            cidadao=self.cidadao,
            cpf_cidadao_snapshot=self.cidadao.cpf,
            nome_cidadao_snapshot=self.cidadao.nome_completo,
            logradouro='Rua das Flores',
            rua='Rua das Flores',
            bairro='Centro',
            ponto_referencia='Próximo à Praça',
            tipo_defeito=TipoDefeito.POSTE_APAGADO,
            status=StatusOcorrencia.PENDENTE,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM historico_ocorrencias WHERE ocorrencia_id = %s",
                [ocorrencia.id],
            )
            count_inicial = cursor.fetchone()[0]
        self.assertEqual(count_inicial, 0)

        # 1. Muda status de Pendente para Em progresso
        ocorrencia.status = StatusOcorrencia.EM_PROGRESSO
        ocorrencia.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT status_anterior, status_novo FROM historico_ocorrencias WHERE ocorrencia_id = %s ORDER BY id",
                [ocorrencia.id],
            )
            rows = cursor.fetchall()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 'Pendente')
        self.assertEqual(rows[0][1], 'Em progresso')

        # 2. Atualização em outro campo sem mudar status não deve disparar o trigger
        ocorrencia.descricao = 'Nova observação sem mudança de status'
        ocorrencia.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM historico_ocorrencias WHERE ocorrencia_id = %s",
                [ocorrencia.id],
            )
            count_apos_descricao = cursor.fetchone()[0]
        self.assertEqual(count_apos_descricao, 1)

        # 3. Muda status de Em progresso para Concluído
        ocorrencia.status = StatusOcorrencia.CONCLUIDO
        ocorrencia.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT status_anterior, status_novo FROM historico_ocorrencias WHERE ocorrencia_id = %s ORDER BY id",
                [ocorrencia.id],
            )
            rows = cursor.fetchall()

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][0], 'Em progresso')
        self.assertEqual(rows[1][1], 'Concluído')

    def test_view_painel_ocorrencias_ativas_filtra_apenas_pendente_e_em_progresso(self):
        oc_pendente = Ocorrencia.objects.create(
            protocolo='TRG222222',
            numero_poste='PST2222',
            cidadao=self.cidadao,
            cpf_cidadao_snapshot=self.cidadao.cpf,
            nome_cidadao_snapshot=self.cidadao.nome_completo,
            logradouro='Av Fernandes Lima',
            rua='Av Fernandes Lima',
            bairro='Farol',
            ponto_referencia='Em frente ao Hospital',
            tipo_defeito=TipoDefeito.LUZ_OSCILANDO,
            status=StatusOcorrencia.PENDENTE,
        )

        oc_progresso = Ocorrencia.objects.create(
            protocolo='TRG333333',
            numero_poste='PST3333',
            cidadao=self.cidadao,
            cpf_cidadao_snapshot=self.cidadao.cpf,
            nome_cidadao_snapshot=self.cidadao.nome_completo,
            logradouro='Av Menino Marcelo',
            rua='Av Menino Marcelo',
            bairro='Serraria',
            ponto_referencia='Posto de Gasolina',
            tipo_defeito=TipoDefeito.ESTRUTURA_DANIFICADA,
            status=StatusOcorrencia.EM_PROGRESSO,
        )

        oc_concluido = Ocorrencia.objects.create(
            protocolo='TRG444444',
            numero_poste='PST4444',
            cidadao=self.cidadao,
            cpf_cidadao_snapshot=self.cidadao.cpf,
            nome_cidadao_snapshot=self.cidadao.nome_completo,
            logradouro='Rua do Comércio',
            rua='Rua do Comércio',
            bairro='Centro',
            ponto_referencia='Galeria Central',
            tipo_defeito=TipoDefeito.POSTE_APAGADO,
            status=StatusOcorrencia.CONCLUIDO,
        )

        oc_excluido = Ocorrencia.objects.create(
            protocolo='TRG555555',
            numero_poste='PST5555',
            cidadao=self.cidadao,
            cpf_cidadao_snapshot=self.cidadao.cpf,
            nome_cidadao_snapshot=self.cidadao.nome_completo,
            logradouro='Rua Antiga',
            rua='Rua Antiga',
            bairro='Poço',
            ponto_referencia='Antiga Padaria',
            tipo_defeito=TipoDefeito.POSTE_APAGADO,
            status=StatusOcorrencia.EXCLUIDO_CIDADAO,
        )

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT protocolo, numero_poste, logradouro, rua, bairro, ponto_referencia,
                       tipo_defeito, status, cidadao_id, nome_completo, cpf
                FROM vw_painel_ocorrencias_ativas
                WHERE protocolo IN ('TRG222222', 'TRG333333', 'TRG444444', 'TRG555555')
                ORDER BY protocolo
            """)
            linhas = cursor.fetchall()

        protocolos_retornados = [linha[0] for linha in linhas]
        self.assertIn('TRG222222', protocolos_retornados)
        self.assertIn('TRG333333', protocolos_retornados)
        self.assertNotIn('TRG444444', protocolos_retornados)
        self.assertNotIn('TRG555555', protocolos_retornados)

        # Checa campos retornados
        linha_pendente = next(l for l in linhas if l[0] == 'TRG222222')
        self.assertEqual(linha_pendente[1], 'PST2222')
        self.assertEqual(linha_pendente[4], 'Farol')
        self.assertEqual(linha_pendente[7], 'Pendente')
        self.assertEqual(linha_pendente[8], self.cidadao.id)
        self.assertEqual(linha_pendente[9], self.cidadao.nome_completo)
        self.assertEqual(linha_pendente[10], self.cidadao.cpf)

    def test_constraint_nome_completo_minimo_3_caracteres(self):
        if connection.vendor != 'postgresql':
            self.skipTest('Constraint CHECK suportada no PostgreSQL')

        from django.db import IntegrityError, transaction

        # Nome com menos de 3 caracteres deve ser rejeitado pelo banco
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Usuario.objects.create_user(
                    username='usuario_curto',
                    cpf='99988877766',
                    nome_completo='Ab',
                    email='curto@teste.com',
                    tipo_perfil=TipoPerfil.CIDADAO,
                )

        # Nome com 3 caracteres ou mais deve ser aceito
        valido = Usuario.objects.create_user(
            username='usuario_valido_3',
            cpf='99988877765',
            nome_completo='Ana',
            email='ana@teste.com',
            tipo_perfil=TipoPerfil.CIDADAO,
        )
        self.assertEqual(valido.nome_completo, 'Ana')

    def test_constraint_status_ocorrencias_aceita_apenas_valores_permitidos(self):
        if connection.vendor != 'postgresql':
            self.skipTest('Constraint CHECK suportada no PostgreSQL')

        from django.db import IntegrityError, transaction

        # Status inválido deve falhar na constraint CHECK
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Ocorrencia.objects.create(
                    protocolo='CHK999999',
                    numero_poste='PST9999',
                    cidadao=self.cidadao,
                    cpf_cidadao_snapshot=self.cidadao.cpf,
                    nome_cidadao_snapshot=self.cidadao.nome_completo,
                    logradouro='Rua do Teste',
                    rua='Rua do Teste',
                    bairro='Centro',
                    ponto_referencia='Próximo à Praça',
                    tipo_defeito=TipoDefeito.POSTE_APAGADO,
                    status='STATUS_TOTALMENTE_INVALIDO',
                )

        # Status permitidos ("Pendente", "Em progresso", "Concluído", "Excluído") devem ser aceitos
        for idx, status_valido in enumerate(['Pendente', 'Em progresso', 'Concluído', 'Excluído']):
            oc = Ocorrencia.objects.create(
                protocolo=f'CHK{idx:06d}',
                numero_poste='PST0001',
                cidadao=self.cidadao,
                cpf_cidadao_snapshot=self.cidadao.cpf,
                nome_cidadao_snapshot=self.cidadao.nome_completo,
                logradouro='Rua do Teste',
                rua='Rua do Teste',
                bairro='Centro',
                ponto_referencia='Próximo à Praça',
                tipo_defeito=TipoDefeito.POSTE_APAGADO,
                status=status_valido,
            )
            self.assertEqual(oc.status, status_valido)

