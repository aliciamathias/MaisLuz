# Spec 0003: Ocorrências de Iluminação Pública

- **Status:** Implementado
- **Requisitos:** RF003, RF005, RF006 e RF007 do [PRD 0001](../prd/0001-maisluz.md)
- **Decisões:** [ADR 0001](../adr/0001-mvt-com-camada-de-service.md), [ADR 0004](../adr/0004-postgresql-como-banco-de-dados.md)
- **Depende de:** [Spec 0001](0001-fundacao.md), [Spec 0002](0002-autenticacao.md)

## Modelo `Ocorrencia` (`ocorrencias/models.py`)

| Campo | Tipo | Regras |
|---|---|---|
| `protocolo` | `CharField(max_length=10, unique=True)` | Gerado pelo service (ex: `#2026-8941`) e imutável |
| `cidadao` | `ForeignKey(settings.AUTH_USER_MODEL, on_delete=PROTECT, null=True, blank=True)` | Solicitante (cidadão identificado). `PROTECT` resguarda integridade histórica |
| `atendente` | `ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True)` | Operador responsável pelo atendimento |
| `numero_poste` | `CharField(max_length=10)` | Identificação física do poste (8 a 10 dígitos) |
| `logradouro` | `CharField(max_length=100)` | Tipo e identificador do logradouro |
| `rua` | `CharField(max_length=100)` | Nome da rua ou avenida |
| `bairro` | `CharField(max_length=100)` | Bairro em Maceió/AL |
| `ponto_referencia` | `CharField(max_length=200)` | Ponto de referência obrigatório |
| `tipo_defeito` | `CharField(choices=TipoDefeito.choices)` | `POSTE_APAGADO`, `LUZ_OSCILANDO` ou `ESTRUTURA_DANIFICADA` |
| `status` | `CharField(choices=StatusOcorrencia.choices)` | `PENDENTE`, `EM_PROGRESSO`, `CONCLUIDO` ou `CANCELADO` |
| `descricao` | `CharField(max_length=300, blank=True)` | Detalhamento opcional |
| `foto` | `ImageField(upload_to="ocorrencias/", null=True, blank=True)` | Imagem opcional do poste |
| `ativo` | `BooleanField(default=True)` | Controle de exclusão lógica |
| `anonimizado` | `BooleanField(default=False)` | Resguardo de privacidade conforme LGPD |
| `criado_em` | `DateTimeField(auto_now_add=True)` | Data e hora de abertura do chamado |
| `atualizado_em` | `DateTimeField(auto_now=True)` | Data da última alteração de status |

## Exceções (`ocorrencias/exceptions.py`)

- `OcorrenciaNaoEncontradaErro`: ocorrência inexistente ou com protocolo inválido.
- `NumeroPosteInvalidoErro`: número de identificação fora do padrão de 8 a 10 dígitos.
- `DadosInsuficientesErro`: ausência de campos essenciais de localização.
- `OcorrenciaEmAndamentoErro`: tentativa de cancelamento de chamado que já está em manutenção ou concluído.
- `PermissaoOcorrenciaNegadaErro`: cidadão tentando alterar chamado que não pertence ao seu CPF.

## `OcorrenciaService` (`ocorrencias/services/ocorrencia.py`)

| Método | Regra |
|---|---|
| `criar_ocorrencia(...)` | Cria novo chamado com protocolo único, status `PENDENTE`, valida dados e registra auditoria |
| `listar_para_cidadao(usuario)` | Retorna ocorrências ativas abertas pelo cidadão ordenadas por `-criado_em` |
| `listar_para_painel(...)` | Retorna chamados para visão dos atendentes e administradores, com filtros de status e bairro |
| `obter_por_protocolo(protocolo)` | Localiza a ocorrência ou levanta `OcorrenciaNaoEncontradaErro` |
| `atualizar_status(ocorrencia, operador, novo_status)` | Altera o status da ocorrência e registra histórico de auditoria |
| `excluir_logica_cidadao(ocorrencia, cidadao)` | Permite cancelamento pelo cidadão apenas se status for `PENDENTE` |

## Formulário (`ocorrencias/forms/ocorrencia.py`)

`RegistroOcorrenciaForm` valida campos obrigatórios, tamanho do número do poste (8 a 10 caracteres) e limites de tamanho de descrição.

## Rotas

| Rota | Nome | View | Métodos | Acesso |
|---|---|---|---|---|
| `/ocorrencias/registrar/` | `registrar_ocorrencia` | `RegistrarOcorrenciaView` | GET, POST | Cidadão autenticado |
| `/ocorrencias/minhas/` | `minhas_ocorrencias` | `MinhasOcorrenciasView` | GET, POST | Cidadão autenticado |
| `/ocorrencias/painel/` | `ocorrencias_painel` | `PainelOcorrenciasView` | GET | Atendente / Administrador |

## Exemplos de View

### Leitura

```python
class MinhasOcorrenciasView(LoginRequiredMixin, View):
    def get(self, request):
        ocorrencias = OcorrenciaService.listar_para_cidadao(request.user)
        return render(
            request,
            "ocorrencias/minhas-ocorrencias-cidadao.html",
            {"ocorrencias": ocorrencias},
        )
```

### Alteração com conversão de exceção em resposta HTTP

```python
class CancelarOcorrenciaView(LoginRequiredMixin, View):
    def post(self, request, protocolo):
        try:
            OcorrenciaService.excluir_logica_cidadao(protocolo, request.user)
        except OcorrenciaNaoEncontradaErro as exc:
            raise Http404 from exc
        except OcorrenciaEmAndamentoErro as exc:
            messages.error(request, str(exc))
            return redirect("minhas_ocorrencias")
        messages.success(request, "Ocorrência cancelada com sucesso.")
        return redirect("minhas_ocorrencias")
```

## Testes

- [x] Criação de ocorrência gera protocolo único e status `PENDENTE`.
- [x] Número do poste menor que 8 ou maior que 10 dígitos gera `"Número de identificação do poste incorreta"`.
- [x] Ocorrência em andamento não pode ser cancelada pelo cidadão.
- [x] Visitante não autenticado tentando registrar ocorrência é redirecionado para login.
- [x] Sucesso no registro exibe `"Ocorrência registrada com sucesso! O chamado foi encaminhado para a empresa de energia."`.
