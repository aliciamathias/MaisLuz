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
- Suíte completa de 65 testes automatizados executando com 100% de aprovação (OK).

## Próximos passos

- Integrar fluxo administrativo e de atendentes (painel corporativo de ocorrências e gestão de operadores).

## Pendências

- Antes de um deploy real (revisão OWASP de 2026-11-04):
  - Limitar tentativas de login e envios de formulário.
  - Tirar `DEBUG = True` do código, preencher `ALLOWED_HOSTS` e resolver os avisos de `check --deploy`.
  - Registrar falhas de login e acessos negados com `LOGGING`.
- Melhoria menor de segurança: adicionar CSP.
