# Estado atual

Atualizado em: 2026-11-11

Este arquivo guarda apenas o que não está em outro lugar. Mantenha-o com cerca de 30 linhas e retire o que estiver resolvido. O status de cada documento fica no próprio documento, e o histórico fica no Git.

## Em andamento

Nada.

## Próximos passos

- Configurar conexão com PostgreSQL e dependência do driver (`psycopg`) em `core/settings.py` e `.env`.
- Elaborar especificações técnicas em `docs/specs/` para o projeto MaisLuz.
- Aplicar diretrizes de frontend (acessibilidade WCAG 2.1 AA e padrões de modularização/CSS) nos templates e arquivos estáticos.

## Pendências

- Antes de um deploy real (revisão OWASP de 2026-11-04):
  - Limitar tentativas de login e envios de comentário, que o PRD deixou fora do escopo.
  - Tirar `DEBUG = True` do código, preencher `ALLOWED_HOSTS` e resolver os avisos de `check --deploy`.
  - Registrar falhas de login e acessos negados, pois não há `LOGGING` configurado.
- Melhoria menor de segurança: adicionar CSP.
- As publicações iniciais usam "admin" como autor e têm todas a mesma data.
- O painel, o login e o tema claro não foram conferidos no navegador depois da mudança de estilo.
