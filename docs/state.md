# Estado atual

Atualizado em: 2026-11-19

Este arquivo guarda apenas o que não está em outro lugar. Mantenha-o com cerca de 30 linhas e retire o que estiver resolvido. O status de cada documento fica no próprio documento, e o histórico fica no Git.

## Em andamento

Nada.

## Próximos passos

- Configurar conexão com PostgreSQL em `core/settings.py` e `.env`.
- Elaborar especificações técnicas em `docs/specs/` para o projeto MaisLuz.
- Implementar as regras de negócio nos services para persistência real das ocorrências e atendentes.
- Implementar as demais telas do Figma marcadas como "ready for dev" nos próximos lotes.

## Pendências

- Antes de um deploy real (revisão OWASP de 2026-11-04):
  - Limitar tentativas de login e envios de formulário.
  - Tirar `DEBUG = True` do código, preencher `ALLOWED_HOSTS` e resolver os avisos de `check --deploy`.
  - Registrar falhas de login e acessos negados com `LOGGING`.
- Melhoria menor de segurança: adicionar CSP.
- Remover/atualizar ADR 0003 remanescente do antigo blog.
