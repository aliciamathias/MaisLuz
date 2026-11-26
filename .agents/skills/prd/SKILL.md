---
name: prd
description: Como escrever requisitos de produto neste projeto. Use ao criar ou alterar um PRD em docs/prd/, ou ao adicionar, mudar ou retirar requisitos e itens fora do escopo.
---

# Diretrizes para Requisitos de Produto (PRD) — Sistema MaisLuz

Este documento estabelece as diretrizes e convenções obrigatórias para especificação, estruturação e manutenção de requisitos de produto (PRD) no projeto **MaisLuz**, baseado no documento formal de engenharia de requisitos do sistema.

Um PRD descreve o que o produto faz, para quem e por quê. O detalhamento técnico de implementação fica nas especificações funcionais (`docs/specs/`) e decisões de arquitetura (`docs/adr/`).

---

## 1. Contexto e Escopo do Sistema MaisLuz

O **MaisLuz** é uma plataforma web com abrangência geográfica estritamente delimitada ao município de **Maceió**, atuando como ponte direta de comunicação entre o cidadão e a concessionária de energia ou órgão público responsável pela iluminação pública.

- **Objetivo central:** Viabilizar que cidadãos previamente identificados via CPF registrem ocorrências detalhadas de falhas em postes de iluminação e acompanhem seus chamados, enquanto operadores/funcionários visualizam, filtram e atualizam o status desses chamados em um painel corporativo centralizado.
- **Limites estritos de escopo:** O sistema cumpre o papel de canal externo de notificação e transparência. **Não engloba nem interfere** nos processos operacionais internos de manutenção da concessionária, roteirização de equipes de campo, gestão de estoque ou ordens de serviço internas.

---

## 2. Convenções e Notação de Identificação de Requisitos

A referência e o registro de requisitos seguem convenções padronizadas e rastreáveis:

### 2.1 Identificadores Padronizados

- **Requisitos Funcionais:** `RFxxx` (ex: `RF001`, `RF002`, `RF003`, ..., sequencial com 3 dígitos). Na referência contextual, utiliza-se a notação `[Nome da Subseção.RFxxx]` (ex: `[Cadastro Cidadão.RF001]`).
- **Requisitos Não Funcionais:** `RNFxx` ou `NFxxx` (ex: `[RNF01]` ou `[Confiabilidade.NF008]`), categorizados por Usabilidade, Abrangência, Segurança/Privacidade, Plataforma/Acesso e Tempo de Reação.
- **Requisitos de Segurança:** `RSxxx` (ex: `[RS001]`).

> **Regra de Imutabilidade:** Nunca renumere nem reaproveite códigos de requisitos existentes, pois especificações (`docs/specs/`), matrizes de rastreabilidade e testes referenciam esses identificadores. Requisitos novos recebem o próximo número disponível.

### 2.2 Classificação de Prioridades

Todo requisito funcional e não funcional deve ser categorizado em um dos três níveis:

1. **Essencial:** Requisito imprescindível sem o qual o sistema não entra em funcionamento. Deve ser implementado impreterivelmente na versão inicial.
2. **Importante:** Requisito sem o qual o sistema opera, mas de forma insatisfatória. Deve ser priorizado para implantação.
3. **Desejável:** Requisito que não compromete as operações básicas. Pode ser postergado para versões subsequentes caso não haja tempo hábil.

---

## 3. Estrutura Obrigatória de um Requisito Funcional

Cada requisito funcional (`RFxxx`) deve ser formalizado detalhando:

1. **Atores Envolvidos:** Quem executa e interage (ex: Cidadão devidamente autenticado, Funcionário/Operador, Administrador).
2. **Entradas e Campos:** Especificação formal de cada campo:
   - Nome do campo.
   - Tipo de dado (`String`, `Inteiro`, `Seleção única`, `Imagem`, `Serial`).
   - Quantidade de caracteres / Limites mínimo e máximo.
   - Obrigatoriedade (`obrigatório` ou `opcional`).
   - Formato ou máscara visual (ex: `XXX.XXX.XXX-XX`, `(XX)9XXXX-XXXX`, `00000-000`).
3. **Regras de Negócio e Validações:**
   - Critérios de preenchimento e integridade (tamanho mínimo de nome, validação de formato de e-mail com `@` e `.`, verificação de DDD e dígitos de telefone, comprimento de senhas de 8 a 30 caracteres, número de identificação do poste de 8 a 10 dígitos na faixa amarela).
   - Fluxo de verificação de contato: envio de token aleatório de 4 dígitos via webservice para e-mail e telefone/SMS, com expiração em 5 minutos.
   - Imutabilidade cadastral (CPF do cidadão e Matrícula Funcional do operador tornam-se estritamente imutáveis após cadastro).
4. **Respostas do Sistema e Mensagens Literais:**
   - Mensagens exatas para erros de validação (ex: `"CPF não identificado"`, `"CPF já cadastrado"`, `"Nome muito curto"`, `"A senha é muito curta"`, `"A senha é muito longa"`, `"As senhas são diferentes"`, `"CEP muito curto"`, `"CEP muito longo"`, `"Número de identificação do poste incorreta"`, `"Usuário ou senha inválidos"`, `"Não foi dada informações o suficiente"`).
   - Confirmações de sucesso e redirecionamentos pós-operação (ex: `"Cadastro realizado com sucesso"`, `"Ocorrência registrada com sucesso! O chamado foi encaminhado para a empresa de energia."`).
   - Comportamento de cancelamento com diálogo de confirmação (`"Todas as alterações serão perdidas. Deseja realmente cancelar?"` com opções Sim/Não).
5. **Ciclo de Vida do Registro:**
   - **Alteração:** Quem pode alterar e obrigatoriedade de histórico de auditoria (responsável, operação realizada, data e hora).
   - **Exclusão:** Sempre **exclusão lógica** — para Cidadão, anonimização dos dados pessoais preservando os registros físicos de ocorrências vinculados; para Funcionário, inativação do status de acesso sem exclusão física para resguardo de auditoria.
   - **Pesquisa e Filtros:** Campos pelos quais a entidade pode ser localizada e ordenação padrão paginada (10 registros por página, ordem decrescente por data de registro).

---

## 4. Requisitos Não Funcionais e Segurança

Os requisitos não funcionais e de segurança devem mapear:

- **[RNF01] Usabilidade:** Interface intuitiva com orientações claras para identificação física do poste e destaque visual de mensagens de erro por campo.
- **[RNF02] Abrangência Geográfica:** Restrição operacional estrita aos limites territoriais do município de Maceió.
- **[RNF03] Privacidade e Criptografia:** Armazenamento seguro de senhas com hash criptográfico irreversível e caracteres mascarados na interface para impedir captura visual.
- **[RNF04] Compatibilidade e Plataforma:** Interface web responsiva acessível em navegadores desktop e dispositivos móveis (smartphones) para viabilizar registros rápidos em campo.
- **[RNF05] Tempo de Reação / Desempenho:** Tempo de resposta às requisições e carregamento de telas/painéis em no máximo 2 segundos sob condições normais de uso.
- **[RS001] Proteção de Credenciais:** Políticas de segurança contra vazamento e visualização direta de senhas.

---

## 5. Artefatos Complementares de Engenharia de Requisitos

Ao documentar novos módulos ou revisar os existentes, mantenha a integração com os artefatos formais:

1. **Matriz de Avaliação de Risco:** Cruzamento de Probabilidade (Frequente, Provável, Ocasional, Remoto, Improvável, Eliminado) por Severidade de Impacto (Catastrófico, Crítico, Marginal, Insignificante).
2. **Matriz de Rastreabilidade:** Mapeamento bidirecional indicando dependências (`D`) e relações (`R`) entre requisitos funcionais (ex: RF001 alimenta RF002, RF005 vincula RF001 ao painel RF006 e RF007).
3. **Análise de Pontos de Função (APF):** Classificação funcional entre Funções de Dados (ALI — Arquivo Lógico Interno, AIE — Arquivo de Interface Externa) e Funções de Transação (EE — Entrada Externa, SE — Saída Externa, CE — Consulta Externa) ponderadas por complexidade (Baixa, Média, Alta).

---

## 6. Estrutura do Arquivo PRD

Os documentos de requisitos devem residir em `docs/prd/NNNN-titulo-em-kebab-case.md` seguindo o modelo:

```markdown
# PRD NNNN: Título do Sistema ou Módulo

- **Status:** Proposto | Aceito | Substituído
- **Data:** AAAA-MM-DD
- **Autores / Responsáveis:** Nomes
- **Especificações:** Links para `docs/specs/` correspondentes

## 1. Introdução e Visão Geral
Contextualização do produto, objetivos, público-alvo e problema que resolve.

## 2. Escopo e Limitações
Delimitação geográfica (Maceió) e o que está expressamente fora do escopo operacional.

## 3. Perfis de Usuário
Tabela detalhando cada ator (Cidadão, Funcionário/Operador, Administrador), identificação necessária e permissões.

## 4. Requisitos Funcionais
Requisitos estruturados individualmente com código [Subseção.RFxxx], prioridade, campos, regras de validação, mensagens literais e operações de CRUD/Pesquisa.

## 5. Requisitos Não Funcionais e de Segurança
Requisitos categorizados ([RNFxx], [RSxx]), descrição mensurável e nível de prioridade (Essencial / Importante / Desejável).

## 6. Matrizes de Suporte
- Matriz de Rastreabilidade entre requisitos.
- Matriz de Avaliação de Risco.
- Estimativa / Contagem de Pontos de Função.

## 7. Critérios de Conclusão e Homologação
Lista de condições verificáveis e testáveis para entrega e validação do sistema.
```

---

## 7. Regras e Boas Práticas

- **Requisitos Verificáveis:** Cada requisito deve ser redigido de modo a permitir cobertura direta por testes automatizados (unitários, integração e frontend).
- **Sem Jargões de Implementação Interna:** Descreva comportamento observável, regras de negócio e validações sem citar nomes de tabelas SQL, classes Python, rotas ou bibliotecas específicas.
- **Mensagens Literais:** Documente as mensagens exatas esperadas na interface para que os testes e templates mantenham 100% de conformidade.
- **Sincronização Contínua:** Ao alterar ou adicionar qualquer requisito, atualize imediatamente as especificações em `docs/specs/` e o documento `docs/state.md`.
