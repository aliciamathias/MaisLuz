# ADR 0004: SQLite como banco de dados

- **Status:** Aceito
- **Data:** 2026-11-04

## Contexto

O projeto já está configurado com SQLite, e o deploy em produção está fora do escopo da primeira versão ([PRD 0001](../prd/0001-blog.md)).

## Decisão

Manter o SQLite. O código usa o ORM do Django e evita SQL específico de um banco, deixando a troca possível.

## Consequências

- Não há serviço de banco para instalar ou configurar.
- O SQLite permite apenas uma escrita por vez, o que é aceitável neste estágio, mas não para um site com muitas escritas simultâneas.
- Um deploy em produção deve reavaliar esta decisão em uma nova ADR.
- O arquivo `db.sqlite3` não deve ser versionado.
