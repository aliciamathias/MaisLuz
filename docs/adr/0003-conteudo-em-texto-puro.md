# ADR 0003: Descrição das ocorrências em texto puro

- **Status:** Aceito
- **Data:** 2026-11-04

## Contexto

A descrição de uma ocorrência reportada pelo cidadão pode ser guardada como texto puro, Markdown ou HTML. Markdown e HTML permitem mais formatação, mas exigem dependências adicionais e sanitização para evitar XSS.

## Decisão

O texto é guardado como texto puro (com limite de até 300 caracteres) e exibido com o autoescape padrão do Django. O filtro `safe` e a função `mark_safe` não são usados em nenhum conteúdo enviado por usuários.

## Consequências

- Não há novas dependências, e o risco de XSS pelo conteúdo fica coberto pelo autoescape nativo do Django.
- A descrição é direta e concisa, sem formatações complexas ou tags maliciosas.
- A integridade dos dados registrados pelo cidadão é preservada.
