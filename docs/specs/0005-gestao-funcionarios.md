# Spec 0005: Gestão de Funcionários e Acessos

- **Status:** Proposto
- **Requisitos:** RF004, RF009 e RF011 do [PRD 0001](../prd/0001-maisluz.md)
- **Decisões:** [ADR 0001](../adr/0001-mvt-com-camada-de-service.md), [ADR 0002](../adr/0002-modelo-de-usuario-customizado.md)
- **Depende de:** [Spec 0001](0001-fundacao.md), [Spec 0002](0002-autenticacao.md), [Spec 0004](0004-auditoria.md)

## Regras de Gestão de Colaboradores

O Administrador é o único perfil com permissão para gerenciar operadores do sistema (atendentes e gestores):

1. **Cadastro de Atendente (RF004):**
   - Matrícula funcional obrigatória (até 20 caracteres) e imutável após cadastro.
   - Cargo definido a partir de escolhas fechadas (`Atendente`, `Gestor de Sistema`, etc.).
   - Geração de credencial com registro de auditoria.

2. **Inativação e Bloqueio de Acesso (RF009):**
   - Administrador pode alterar o `status_acesso` de um usuário para `INATIVO` ou `BLOQUEADO`.
   - Usuário inativo ou bloqueado é impedido de efetuar login pelo backend de autenticação.
   - Cada bloqueio ou inativação gera evento obrigatório no `HistoricoAuditoria`.

3. **Recuperação de Senha (RF011):**
   - **Cidadão:** fluxo externo com validação de CPF/e-mail e código temporário.
   - **Funcionário:** solicitação encaminhada ao Administrador/suporte técnico para redefinição segura com registro de auditoria.

## Rotas

| Rota | Nome | View | Métodos | Acesso |
|---|---|---|---|---|
| `/funcionarios/cadastro/` | `cadastro_atendente` | `CadastroAtendenteView` | GET, POST | Administrador |
| `/funcionarios/editar/` | `editar_atendente` | `EditarAtendenteView` | GET, POST | Administrador |
| `/perfil/` | `meu_perfil_interno` | `MeuPerfilInternoView` | GET, POST | Atendente / Administrador |
| `/contas/recuperar-senha/cidadao/` | `recuperar_senha_cidadao` | `RecuperarSenhaCidadaoView` | GET, POST | Público |
| `/contas/recuperar-senha/atendente/` | `recuperar_senha_atendente` | `RecuperarSenhaAtendenteView` | GET, POST | Funcionário |

## Testes

- [x] Matrícula funcional é única e imutável.
- [x] Usuário bloqueado não consegue efetuar login.
- [x] Alteração de status gera registro em `HistoricoAuditoria`.
