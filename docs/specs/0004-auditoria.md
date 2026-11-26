# Spec 0004: Auditoria e Rastreabilidade

- **Status:** Implementado
- **Requisitos:** RF010 e RF012 do [PRD 0001](../prd/0001-maisluz.md)
- **Decisões:** [ADR 0001](../adr/0001-mvt-com-camada-de-service.md), [ADR 0004](../adr/0004-postgresql-como-banco-de-dados.md)
- **Depende de:** [Spec 0002](0002-autenticacao.md), [Spec 0003](0003-ocorrencias.md)

## Modelo `HistoricoAuditoria` (`contas/models/auditoria.py`)

Garante a imutabilidade e a rastreabilidade completa de todas as operações administrativas e operacionais:

| Campo | Tipo | Regras |
|---|---|---|
| `usuario` | `ForeignKey(settings.AUTH_USER_MODEL, on_delete=PROTECT, null=True, blank=True)` | Autor da ação. `PROTECT` impede que exclusão de contas apague registros de auditoria |
| `ocorrencia` | `ForeignKey("ocorrencias.Ocorrencia", on_delete=PROTECT, null=True, blank=True)` | Chamado relacionado (quando aplicável) |
| `tipo_operacao` | `CharField(max_length=60)` | Identificador da operação (ex: criação de conta, alteração de status, inativação) |
| `detalhes` | `TextField()` | Descrição textual dos dados antes e depois da alteração |
| `criado_em` | `DateTimeField(auto_now_add=True)` | Data e hora exatas do evento |

## `AuditoriaService` (`contas/services/auditoria.py`)

| Método | Regra |
|---|---|
| `registrar(usuario, tipo_operacao, detalhes, ocorrencia=None)` | Cria um registro imutável no histórico de auditoria |
| `listar_por_ocorrencia(ocorrencia)` | Retorna o histórico de eventos de uma ocorrência ordenado por `-criado_em` |
| `listar_por_usuario(usuario)` | Retorna as ações realizadas pelo operador ou modificações cadastrais do cidadão |

## Regras de Negócio

1. **Rastreabilidade de Mudanças de Status (RF012):** Toda alteração de status (`PENDENTE` -> `EM_PROGRESSO` -> `CONCLUIDO` / `CANCELADO`) registra quem executou a mudança e a justificativa.
2. **Imutabilidade e Não Exclusão:** Registros de auditoria nunca são excluídos do banco de dados, nem mesmo quando um cidadão solicita exclusão lógica (seus dados são anonimizados, mas o log de auditoria é preservado).

## Testes

- [x] Toda criação de ocorrência registra evento de auditoria com vínculo de usuário e ocorrência.
- [x] Toda atualização de status registra o operador responsável no histórico.
- [x] Exclusão de usuário é bloqueada por `PROTECT` se houver registros vinculados na auditoria.
