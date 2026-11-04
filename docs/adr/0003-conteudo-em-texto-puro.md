# ADR 0003: Conteúdo dos posts em texto puro

- **Status:** Aceito
- **Data:** 2026-11-04

## Contexto

O conteúdo de um post pode ser guardado como texto puro, Markdown ou HTML. Markdown e HTML permitem mais formatação, mas exigem dependências adicionais e sanitização para evitar XSS.

## Decisão

O conteúdo é guardado como texto puro e exibido com o autoescape do Django e o filtro `linebreaks`, que transforma quebras de linha em parágrafos. O filtro `safe` e a função `mark_safe` não são usados em conteúdo enviado por usuários.

## Consequências

- Não há novas dependências, e o risco de XSS pelo conteúdo fica coberto pelo autoescape.
- Os posts não têm títulos internos, links clicáveis, imagens nem outras formatações.
- Adotar Markdown no futuro exigirá uma nova ADR, com renderização e sanitização, mas não exigirá migrar os textos já gravados.
