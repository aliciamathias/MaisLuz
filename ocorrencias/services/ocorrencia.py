import random
from django.db import models, transaction
from django.utils import timezone
from contas.models import HistoricoAuditoria, TipoOperacaoAuditoria
from ocorrencias.exceptions import (
    DadosInsuficientesErro,
    NumeroPosteInvalidoErro,
    OcorrenciaEmAndamentoErro,
    OcorrenciaNaoEncontradaErro,
    PermissaoOcorrenciaNegadaErro,
)
from ocorrencias.models import Ocorrencia, StatusOcorrencia, TipoDefeito


class OcorrenciaService:
    @staticmethod
    def _gerar_protocolo() -> str:
        ano = timezone.now().strftime("%y")
        for _ in range(10):
            sufixo = f"{random.randint(0, 99999999):08d}"
            protocolo = f"{ano}{sufixo}"[:10]
            if not Ocorrencia.objects.filter(protocolo=protocolo).exists():
                return protocolo
        # Fallback sequencial
        total = Ocorrencia.objects.count() + 1
        return f"{ano}{total:08d}"[:10]

    @staticmethod
    @transaction.atomic
    def criar_ocorrencia(
        *,
        cidadao,
        numero_poste: str,
        logradouro: str,
        rua: str,
        bairro: str,
        ponto_referencia: str,
        tipo_defeito: str,
        descricao: str = "",
        foto=None,
    ) -> Ocorrencia:
        if not cidadao or not getattr(cidadao, "is_authenticated", False) or not cidadao.cpf:
            raise PermissaoOcorrenciaNegadaErro("O registro da ocorrência exige cidadão devidamente autenticado com CPF.")

        poste_limpo = (numero_poste or "").strip()
        if len(poste_limpo) < 8 or len(poste_limpo) > 10:
            raise NumeroPosteInvalidoErro("Número de identificação do poste incorreta")

        if not logradouro or not rua or not bairro or not ponto_referencia or not tipo_defeito:
            raise DadosInsuficientesErro("Não foi dada informações o suficiente")

        if not do_choices(tipo_defeito):
            # Normalizar para choices válidos
            tipos_validos = [choice[0] for choice in TipoDefeito.choices]
            if tipo_defeito not in tipos_validos:
                raise DadosInsuficientesErro(f"Tipo de defeito inválido: {tipo_defeito}")

        protocolo = OcorrenciaService._gerar_protocolo()

        ocorrencia = Ocorrencia(
            protocolo=protocolo,
            numero_poste=poste_limpo,
            cidadao=cidadao,
            cpf_cidadao_snapshot=cidadao.cpf,
            nome_cidadao_snapshot=cidadao.nome_completo or cidadao.get_full_name() or cidadao.username,
            logradouro=logradouro[:100],
            rua=rua[:100],
            bairro=bairro[:100],
            ponto_referencia=ponto_referencia[:200],
            tipo_defeito=tipo_defeito,
            descricao=(descricao or "")[:300],
            foto=foto,
            status=StatusOcorrencia.PENDENTE,
        )
        ocorrencia.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=cidadao,
            identificador_afetado=cidadao.cpf,
            ocorrencia=ocorrencia,
            protocolo_ocorrencia=protocolo,
            operador=cidadao,
            identificador_operador=cidadao.cpf,
            tipo_operacao=TipoOperacaoAuditoria.ATUALIZACAO_STATUS_OCORRENCIA,
            detalhes={
                "acao": "Criação de ocorrência",
                "protocolo": protocolo,
                "numero_poste": poste_limpo,
                "status": StatusOcorrencia.PENDENTE,
            },
        )
        return ocorrencia

    @staticmethod
    @transaction.atomic
    def excluir_logica_cidadao(ocorrencia: Ocorrencia, cidadao) -> Ocorrencia:
        if ocorrencia.cidadao_id != cidadao.pk:
            raise PermissaoOcorrenciaNegadaErro("Cidadão não autorizado a alterar esta ocorrência.")

        if ocorrencia.status in [StatusOcorrencia.CONCLUIDO, StatusOcorrencia.EM_PROGRESSO]:
            raise OcorrenciaEmAndamentoErro(
                "Não é possível excluir sua ocorrência agora, ela já está sendo trabalhada"
            )

        ocorrencia.status = StatusOcorrencia.EXCLUIDO_CIDADAO
        ocorrencia.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=cidadao,
            identificador_afetado=cidadao.cpf or cidadao.username,
            ocorrencia=ocorrencia,
            protocolo_ocorrencia=ocorrencia.protocolo,
            operador=cidadao,
            identificador_operador=cidadao.cpf or cidadao.username,
            tipo_operacao=TipoOperacaoAuditoria.EXCLUSAO_OCORRENCIA_CIDADAO,
            detalhes={"protocolo": ocorrencia.protocolo, "status": ocorrencia.status},
        )
        return ocorrencia

    @staticmethod
    @transaction.atomic
    def excluir_logica_funcionario(
        ocorrencia: Ocorrencia,
        funcionario,
        justificativa: str = "",
    ) -> Ocorrencia:
        if not getattr(funcionario, "is_gestor_sistema", False):
            raise PermissaoOcorrenciaNegadaErro(
                "A exclusão lógica de ocorrência somente pode ser realizada por Gestor do Sistema ou Administrador."
            )

        ocorrencia.status = StatusOcorrencia.EXCLUIDO_FUNCIONARIO
        ocorrencia.atendente = funcionario
        ocorrencia.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=ocorrencia.cidadao,
            identificador_afetado=ocorrencia.cpf_cidadao_snapshot or f"Cidadao #{ocorrencia.cidadao_id}",
            ocorrencia=ocorrencia,
            protocolo_ocorrencia=ocorrencia.protocolo,
            operador=funcionario,
            identificador_operador=getattr(funcionario, "matricula_funcional", None) or getattr(funcionario, "cpf", None) or funcionario.username,
            cargo_operador=getattr(funcionario, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.EXCLUSAO_OCORRENCIA_FUNCIONARIO,
            justificativa=justificativa,
            detalhes={"protocolo": ocorrencia.protocolo, "status": ocorrencia.status},
        )
        return ocorrencia

    @staticmethod
    @transaction.atomic
    def atualizar_status(ocorrencia: Ocorrencia, novo_status: str, funcionario) -> Ocorrencia:
        if not getattr(funcionario, "is_funcionario", False):
            raise PermissaoOcorrenciaNegadaErro("Apenas funcionários podem atualizar o status da ocorrência.")

        status_antigo = ocorrencia.status
        ocorrencia.status = novo_status
        ocorrencia.atendente = funcionario
        ocorrencia.save()

        HistoricoAuditoria.objects.create(
            usuario_afetado=ocorrencia.cidadao,
            identificador_afetado=ocorrencia.cpf_cidadao_snapshot or f"Cidadao #{ocorrencia.cidadao_id}",
            ocorrencia=ocorrencia,
            protocolo_ocorrencia=ocorrencia.protocolo,
            operador=funcionario,
            identificador_operador=getattr(funcionario, "matricula_funcional", None) or funcionario.username,
            cargo_operador=getattr(funcionario, "cargo", ""),
            tipo_operacao=TipoOperacaoAuditoria.ATUALIZACAO_STATUS_OCORRENCIA,
            detalhes={
                "protocolo": ocorrencia.protocolo,
                "status_anterior": status_antigo,
                "status_novo": novo_status,
            },
        )
        return ocorrencia

    @staticmethod
    def listar_para_cidadao(cidadao):
        return Ocorrencia.objects.filter(cidadao=cidadao).exclude(
            status=StatusOcorrencia.EXCLUIDO_CIDADAO
        ).order_by("-data_registro")

    @staticmethod
    def listar_para_funcionario(
        *,
        numero_poste: str | None = None,
        bairro: str | None = None,
        status: str | None = None,
        termo_solicitante: str | None = None,
    ):
        qs = Ocorrencia.objects.exclude(status=StatusOcorrencia.EXCLUIDO_FUNCIONARIO)
        if numero_poste:
            qs = qs.filter(numero_poste__icontains=numero_poste.strip())
        if bairro:
            qs = qs.filter(bairro__icontains=bairro.strip())
        if status:
            qs = qs.filter(status=status)
        if termo_solicitante:
            termo = termo_solicitante.strip()
            qs = qs.filter(
                models.Q(nome_cidadao_snapshot__icontains=termo)
                | models.Q(cpf_cidadao_snapshot__icontains=termo)
            )
        return qs.order_by("-data_registro")


def do_choices(tipo_defeito: str) -> bool:
    return tipo_defeito in [choice[0] for choice in TipoDefeito.choices]
