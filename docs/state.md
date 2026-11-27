# Estado atual

Atualizado em: 2026-11-26

Este arquivo guarda apenas o que não está em outro lugar. Mantenha-o com cerca de 30 linhas e retire o que estiver resolvido. O status de cada documento fica no próprio documento, e o histórico fica no Git.

## Em andamento

Nada.

## Concluído recentemente

- Atualização completa de `docs/arquitetura.md` e `docs/specs/` removendo todos os resquícios do antigo sistema de posts e adaptando para o sistema MaisLuz:
  - Exemplos de leitura e alteração atualizados em `docs/arquitetura.md` e `docs/specs/0003-ocorrencias.md` utilizando `OcorrenciaService`, `MinhasOcorrenciasView` e `CancelarOcorrenciaView`.
  - Specs reescritas alinhadas ao PRD do MaisLuz: `0001-fundacao.md`, `0002-autenticacao.md`, `0003-ocorrencias.md`, `0004-auditoria.md` e `0005-gestao-funcionarios.md`.
  - Remoção dos arquivos obsoletos do blog (`0003-posts.md`, `0004-comentarios.md`, `0005-publicacoes-iniciais.md`).
  - Atualização de `docs/adr/0003-conteudo-em-texto-puro.md` e skill de Python para o domínio do MaisLuz.
- Criação e aplicação de trigger, índices e views no banco MaisLuz (PostgreSQL):
  - Tabela `historico_ocorrencias` e trigger `trg_historico_ocorrencias_status` gravando `id`, `status_anterior`, `status_novo` e `data_alteracao` em mudanças de status.
  - Índices otimizados evitando duplicações onde já havia PK ou UNIQUE (`cpf`, `matricula_funcional`, `protocolo`), indexando `email`, `status`, `bairro`, `numero_poste`, `data_registro`.
  - View `vw_painel_ocorrencias_ativas` com dados da ocorrência e cidadão, filtrando status 'Pendente' e 'Em progresso'.
  - Script DDL em `docs/database/triggers_indices_views.sql` e migração `ocorrencias.0003_trigger_indices_views`.
- Criação e configuração de roles RBAC no PostgreSQL (`suporte_maisluz` e `dev_maisluz`):
  - Permissões de SELECT, INSERT e UPDATE nas tabelas e sequências do schema public.
  - Bloqueio explícito de DELETE com REVOKE em todas as tabelas atuais e padrão.
  - Script DDL em `docs/database/roles_permissoes.sql` e comando `python manage.py setup_roles --verify`.
- Criação de constraints CHECK no PostgreSQL:
  - `chk_usuario_nome_completo_min_length`: valida comprimento >= 3 caracteres para cidadãos e funcionários.
  - `chk_ocorrencia_status_valido`: restringe status a 'Pendente', 'Em progresso', 'Concluído' e 'Excluído'.
  - Script DDL em `docs/database/constraints.sql` e migração `ocorrencias.0004_check_constraints`.
- Suíte de 69 testes automatizados executando com 100% de aprovação (OK).

## Próximos passos

- Integrar fluxo administrativo e de atendentes (painel corporativo de ocorrências e gestão de operadores).

## Pendências

- Antes de um deploy real (revisão OWASP de 2026-11-04):
  - Limitar tentativas de login e envios de formulário.
  - Tirar `DEBUG = True` do código, preencher `ALLOWED_HOSTS` e resolver os avisos de `check --deploy`.
  - Registrar falhas de login e acessos negados com `LOGGING`.
- Melhoria menor de segurança: adicionar CSP.
