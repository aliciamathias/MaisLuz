---
name: padroes-frontend
description: Regras de arquitetura, organização de arquivos e boas práticas de frontend para projetos Django. Use ao criar, modularizar ou alterar templates HTML, arquivos parciais e folhas de estilo CSS.
---

# Padrões de Arquitetura Frontend (Django)

Este documento define as regras obrigatórias de organização, estrutura de diretórios e padrões de estilo frontend para o projeto Django, assegurando manutenibilidade, reutilização e clareza de código.

---

## 1. Modularização Obrigatória

Toda interface desenvolvida no projeto deve adotar modularidade estrita:

- **Isolamento de Blocos Comuns:**
  - O cabeçalho global (`header`), o rodapé global (`footer`) e qualquer bloco de interface repetitivo (como barras de navegação, modais, cards de ocorrências, alertas/toasts, tabelas padronizadas e controles de paginação) **devem obrigatoriamente ser isolados em arquivos HTML dedicados**.
- **Reutilização via `{% include %}`:**
  - A inclusão e montagem dos blocos modulares em páginas mestras (como a página base) ou templates de visualização deve ser realizada exclusivamente por meio da tag include do Django, referenciando o caminho do arquivo parcial.
- **Proibição de Duplicação:** É proibido duplicar a estrutura de header, footer ou componentes compartilhados diretamente no corpo de templates de páginas individuais.

---

## 2. Organização de Pastas de Templates

Os arquivos do frontend devem seguir uma taxonomia padronizada e previsível:

- **Diretório de Parciais (`partials` ou `components`):**
  - Todo arquivo de bloco reutilizável ou componente parcial deve residir obrigatoriamente dentro de uma subpasta nomeada `partials/` ou `components/` na pasta de templates correspondente.
- **Estruturação de Diretórios:**
  - A pasta raiz de templates armazena o template base e a pasta de parciais para componentes globais como cabeçalho e rodapé.
  - Cada módulo ou aplicativo armazena seus templates específicos de páginas e, caso possua blocos reutilizáveis locais, mantém sua própria subpasta de parciais.
- **Nomenclatura Recomendada:** Recomenda-se iniciar o nome dos arquivos parciais com sublinhado ou manter nomes descritivos e diretos dentro da pasta de parciais.

---

## 3. Organização de Estilos CSS e Mapeamento 1:1

A relação entre templates HTML e folhas de estilo CSS deve ser direta e unívoca:

- **Correspondência Exata de Nomes:**
  - Cada página HTML deve possuir um arquivo CSS correspondente localizado na pasta `static/css/`, com exatamente o mesmo nome base do template (por exemplo, um template de perfil associa-se à folha de estilos de perfil com extensão CSS).
- **Carregamento via `{% static %}`:**
  - Os arquivos CSS devem ser vinculados nos templates utilizando a tag static do Django dentro do bloco reservado no cabeçalho do documento estendido da página base.
- **Estilos de Componentes Parciais:**
  - Componentes que pertencem a uma página específica devem ter seus estilos no arquivo CSS daquela página.
  - Componentes globais compartilhados (header, footer, botões padrão) devem ter seus estilos consolidados na folha de estilos da página base ou em folhas utilitárias globais.

---

## 4. Cores Repetitivas e Variáveis no CSS Root

Para garantir harmonia visual, facilidade de manutenção e consistência de contraste:

- **Arquivo Central de Variáveis:**
  - Todas as cores repetitivas em formato hexadecimal empregadas no projeto devem ser centralizadas em um único arquivo de estilos raiz: `static/css/root.css` (ou `variables.css`).
- **Declaração sob a pseudo-classe `:root`:**
  - Cada cor deve ser registrada como uma propriedade customizada (variável CSS) com um nome semântico e simplificado, cobrindo a paleta principal, cores de destaque e alerta, tons neutros de superfície e estados do sistema (como sucesso e erro).
- **Consumo Obrigatório via `var()`:**
  - É proibido inserir valores hexadecimais literais repetidos diretamente nas regras de classes ou identificadores em arquivos CSS de páginas e componentes.
  - Todos os estilos devem consumir exclusivamente as variáveis declaradas no arquivo raiz através da função `var()`.
- **Inclusão no Template Base:**
  - O arquivo `root.css` deve ser o primeiro arquivo de estilo carregado no cabeçalho de `base.html`, antes de qualquer outra folha de estilos do projeto.

---

## 5. Responsividade e Adaptação a Dispositivos Móveis

Todas as páginas e componentes do sistema devem ser estritamente responsivos, assegurando uso com total clareza em celulares, tablets e computadores:

- **Adaptação para Celulares e Tablets:**
  - A interface deve ajustar-se automaticamente a diferentes resoluções e proporções de tela, permitindo que cidadãos e operadores acessem e naveguem pelo sistema de forma confortável e sem cortes visuais.
  - O template base deve conter a declaração da meta tag de viewport para controle de largura e escala apropriada em navegadores móveis.
- **Layouts Fluidos e Prevenção de Rolagem Horizontal:**
  - Formulários de cadastro, campos de relato de ocorrências, cards e tabelas de acompanhamento devem reorganizar suas colunas de forma fluida para leitura vertical em dispositivos móveis, sendo terminantemente proibida a ocorrência de barra de rolagem horizontal não planejada.
- **Usabilidade e Áreas de Toque:**
  - Botões, campos de entrada de formulários e controles de ação devem ter dimensões e espaçamentos adequados para toques confortáveis com os dedos em telas sensíveis ao toque de smartphones e tablets.
- **Organização das Regras Responsivas:**
  - As adaptações para diferentes faixas de resolução devem ser implementadas nas folhas de estilo correspondentes a cada página ou componente, utilizando regras de mídia organizadas e fluidas.

