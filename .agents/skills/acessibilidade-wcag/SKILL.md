---
name: acessibilidade-wcag
description: Diretrizes de acessibilidade baseadas na WCAG 2.1 Nível AA e roteiro de auditoria estática de código para frontend Django. Use ao criar, revisar ou alterar templates HTML, formulários, componentes e folhas de estilo CSS.
---

# Diretrizes de Acessibilidade (WCAG 2.1 Nível AA)

Este documento define os padrões obrigatórios de acessibilidade para o desenvolvimento frontend do projeto, garantindo conformidade com a norma **WCAG 2.1 Nível AA**. Como assistente de IA, o modelo deve auditar o código estático (templates HTML e folhas de estilo CSS) para assegurar o cumprimento estrito destas regras.

---

## 1. Estrutura Semântica Obrigatória

O uso de tags semânticas do HTML5 é mandatório para permitir que navegadores e tecnologias assistivas (leitores de tela como NVDA, JAWS e TalkBack) compreendam o papel e a hierarquia dos elementos.

- **Marcos estruturais (Landmarks):**
  - `<header>`: Para cabeçalhos de página e seções.
  - `<nav>`: Para menus de navegação primários e secundários. Deve conter `aria-label` descritivo caso haja mais de um `<nav>` na página (ex: `<nav aria-label="Navegação principal">`).
  - `<main>`: Apenas um elemento `<main>` por página, encapsulando o conteúdo central.
  - `<section>` e `<article>`: Para agrupar conteúdos temáticos ou autônomos. Devem preferencialmente conter um título (`<h2>`-`<h6>`).
  - `<aside>`: Para informações complementares ou laterais.
  - `<footer>`: Para rodapés informativos, links institucionais e direitos autorais.
- **Hierarquia de Cabeçalhos:**
  - Toda página deve possuir exatamente um elemento `<h1>` representativo do conteúdo principal.
  - A hierarquia (`<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>`) deve ser estritamente sequencial. É **proibido pular níveis** (ex: passar de `<h1>` diretamente para `<h3>`).
- **Listas e Agrupamentos:**
  - Itens de navegação, listagens de ocorrências e coleções de dados devem ser estruturados com `<ul>` ou `<ol>` contendo elementos `<li>`.
- **Elementos Interativos Nativos:**
  - Ações (como submeter formulários, alternar abas, abrir modais) devem usar `<button type="button">` ou `<button type="submit">`.
  - Links de navegação para novas páginas ou âncoras devem usar `<a href="...">`.
  - **Proibido:** Usar `<div>`, `<span>` ou `<p>` com eventos `onclick` simulando botões ou links sem a semântica nativa.

---

## 2. Atributos ARIA (`aria-*`) para Leitores de Tela

O uso de ARIA complementa a semântica nativa quando esta não for suficiente (seguindo a Primeira Regra do WAI-ARIA: *Não use ARIA quando uma tag HTML nativa puder cumprir a função*).

- **Identificação e Contexto:**
  - `aria-label`: Usar em botões ou links que contêm apenas ícones gráficos (ex: `<button type="button" aria-label="Fechar janela modal">✕</button>`).
  - `aria-labelledby` e `aria-describedby`: Usar para associar elementos a textos explicativos ou títulos de referência.
- **Estados e Propriedades Dinâmicas:**
  - `aria-expanded="true|false"`: Obrigatório em botões que controlam menus sanfona (accordion), dropdowns ou gavetas colapsáveis.
  - `aria-haspopup="dialog|menu|true"`: Para indicar abertura de menus ou caixas de diálogo.
  - `aria-hidden="true"`: Mandatório em elementos puramente visuais e decorativos (ex: ícones SVG, glifos, divisores visuais), impedindo ruído na leitura assistiva.
- **Notificações e Alertas Dinâmicos:**
  - Mensagens de erro em formulários e alertas (toasts) devem possuir `role="alert"` ou `aria-live="polite"` (ou `"assertive"` para erros críticos), garantindo que sejam anunciadas imediatamente ao leitor de tela.

---

## 3. Associação Obrigatória de Formulários (`<label>` e `<input>`)

Todo controle de formulário deve ter seu rótulo explicitamente associado:

- **Associação Explícita via ID/for:**
  - Todo controle de entrada (`input`, `select` e `textarea`) deve conter um atributo `id` exclusivo.
  - A tag `label` correspondente deve possuir obrigatoriamente o atributo `for` com valor estritamente idêntico ao `id` do campo associado.
- **Rótulos Ocultos (se aplicável por design):**
  - Caso o design exija ocultar visualmente o rótulo, nunca remova o `<label>`. Utilize uma classe acessível de ocultação visual (ex: `.visually-hidden` ou `.sr-only`), mantendo o elemento perceptível para leitores de tela.
- **Indicação de Erros de Validação:**
  - Campos inválidos devem receber `aria-invalid="true"`.
  - A mensagem de erro textual deve ser vinculada ao campo por meio de `aria-describedby="id_do_erro"`.

---

## 4. Navegação por Teclado e Foco (`tabindex`)

A aplicação deve ser 100% operável via teclado, sem exigir o uso de mouse ou toque:

- **Ordem de Tabulação:**
  - A ordem de foco (`Tab` para avançar, `Shift + Tab` para retroceder) deve seguir o fluxo visual e lógico de leitura do documento.
- **Uso Estrito do `tabindex`:**
  - `tabindex="0"`: Utilizar exclusivamente para incluir na navegação natural elementos que precisem receber foco interativo.
  - `tabindex="-1"`: Utilizar em elementos que recebem foco programático via JavaScript (ex: destino de links rápidos, contêiner de modais abertos).
  - **Proibição absoluta:** É terminantemente vedado o uso de `tabindex` positivo (`tabindex="1"`, `tabindex="2"` etc.), pois quebra a ordem natural do DOM e desorienta pessoas que usam navegação assistiva.
- **Indicador de Foco Visível Obrigatório:**
  - É proibido remover a marcação de foco com `outline: none` ou `outline: 0` sem fornecer uma alternativa visual de alto contraste correspondente.
  - O estilo de foco deve ser nítido e destacado em todos os elementos focáveis (ex: `outline: 2px solid var(--azul-foco); outline-offset: 2px;`).
- **Links Rápidos (Skip Links):**
  - As páginas devem incluir no início do `<body>` um link de salto rápido ("Pular para o conteúdo principal"), oculto visualmente e visível ao receber o primeiro foco de tabulação, apontando para `#conteudo-principal` (o elemento `<main>`).

---

## 5. Auditoria Estática de Código pela IA (Checklist de Inspeção)

Ao gerar, revisar ou editar código frontend (templates e CSS), o assistente de IA deve inspecionar estaticamente:

1. **Validação de Tags Semânticas:**
   - [ ] Há apenas um elemento `<main>` no template?
   - [ ] Os cabeçalhos `<h1>` a `<h6>` seguem hierarquia contínua sem pular níveis?
   - [ ] Todos os elementos interativos clicáveis são `<button>` ou `<a>` nativos?
2. **Validação de Formulários e Labels:**
   - [ ] Todo campo possui `<label for="...">` apontando para um `id` existente?
   - [ ] Campos com erro possuem `aria-invalid="true"` e descrição ligada via `aria-describedby`?
3. **Validação de Navegação por Teclado:**
   - [ ] Não há ocorrência de `tabindex` maior que zero no código?
   - [ ] O CSS preserva indicadores claros de `:focus` e `:focus-visible`?
4. **Auditoria de Cores e Contraste em Formato Hexadecimal:**
   - [ ] O contraste entre a cor do texto (`color: #HEX`) e o fundo (`background-color: #HEX`) atende aos parâmetros da WCAG 2.1 AA:
     - **Texto normal (< 18pt / 24px ou < 14pt / 18.66px negrito):** Razão mínima de **4.5:1**.
     - **Texto grande (≥ 18pt / 24px ou ≥ 14pt / 18.66px negrito) e componentes de interface:** Razão mínima de **3.0:1**.
   - [ ] O código não transmite informações ou estados (sucesso, erro, alerta) exclusivamente pela cor. Sempre há um texto, ícone com texto alternativo ou indicador visual complementar.

