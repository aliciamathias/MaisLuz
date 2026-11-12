# ADR 0004: PostgreSQL como banco de dados

- **Status:** Aceito
- **Data:** 2026-11-11

## Contexto

O projeto MaisLuz ([PRD 0001](../prd/0001-maisluz.md)) possui como restrição e requisito obrigatório a utilização do PostgreSQL como sistema gerenciador de banco de dados relacional. O protótipo inicial utilizava SQLite, mas o sistema definitivo deve obrigatoriamente operar sobre o PostgreSQL.

## Decisão

Adotar o PostgreSQL como banco de dados do projeto, em cumprimento ao requisito obrigatório estabelecido. O acesso aos dados continua sendo abstraído pela camada de services por meio do ORM do Django, utilizando o driver `psycopg` (ou `psycopg2`).

## Consequências

- Cumprimento da obrigatoriedade do projeto quanto ao banco de dados.
- Suporte pleno a múltiplas conexões concorrentes de leitura e escrita sem travamento da base.
- Exige instalação, execução e manutenção de um servidor PostgreSQL nos ambientes de desenvolvimento e produção.
- Requer gerenciamento dos parâmetros de conexão (`ENGINE`, `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT`) via variáveis de ambiente no arquivo `.env`.
