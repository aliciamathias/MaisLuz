# PRD 0001: MaisLuz

- **Status:** Aceito
- **Data:** 2026-11-23
- **Autores:** Daniel de Jesus e Alicia Mathias
- **Especificações:** `docs/specs/`

## 1. Introdução e Visão Geral

Este documento especifica os requisitos do sistema **MaisLuz**, fornecendo as diretrizes formais para o projeto, implementação, testes e homologação do software.

O MaisLuz é uma solução desenvolvida em plataforma web com abrangência geográfica estritamente delimitada ao município de Maceió, atuando fundamentalmente como uma ponte de comunicação direta entre o cidadão e a concessionária de energia ou órgão público responsável.

Operacionalmente, a ferramenta viabiliza que os cidadãos — devidamente identificados por meio de cadastro prévio com CPF para coibir denúncias anônimas e trotes — registrem ocorrências detalhadas de problemas na iluminação pública, informando os dados físicos essenciais obtidos diretamente no local (número de identificação do poste, logradouro, bairro e ponto de referência), além da especificação do tipo de defeito constatado (postes apagados, oscilando ou danificados).

Em contrapartida, o sistema centraliza essas informações em um painel dedicado à concessionária ou órgão competente, permitindo a visualização organizada de todos os chamados reportados pela população, otimizando o fluxo de atendimento externo e a prestação de serviços à comunidade.

## 2. Escopo Físico e Limitações

O sistema restringe-se a atuar exclusivamente como canal de atendimento externo para notificação e acompanhamento de falhas na iluminação pública em Maceió. 

### Limitações e Fora do Escopo:
- Não interfere, engloba ou gerencia processos e trâmites internos de manutenção de campo da concessionária.
- Não realiza despacho ou roteirização de equipes operacionais.
- Não gerencia estoque de materiais, peças de reposição ou custos operacionais.
- Não atende ocorrências fora dos limites territoriais de Maceió.
- Não aceita registros de ocorrências anônimas ou sem validação prévia de CPF.

## 3. Perfis de Uso

| Perfil | Quem é | O que precisa fazer |
|---|---|---|
| Cidadão | Morador de Maceió cadastrado e identificado com CPF | Cadastrar-se, autenticar-se, registrar ocorrências com localização e número do poste, acompanhar o status dos seus chamados |
| Funcionário | Colaborador da empresa de energia com matrícula funcional | Autenticar-se, consultar, filtrar, visualizar detalhes completos e atualizar o status das ocorrências |
| Administrador | Gestor institucional da empresa de energia | Cadastrar e gerenciar colaboradores, auditar históricos de alterações e permissões de acesso |

---

## 4. Requisitos Funcionais

### [Cadastro Cidadão.RF001]
- **Prioridade:** Essencial
- **Descrição:** Permite o cadastramento de cidadãos que acessarão o sistema para notificar falhas em postes de iluminação pública.
- **Campos de Entrada:**
  - `CPF`: String, 14 caracteres, obrigatório (`XXX.XXX.XXX-XX`).
  - `Nome completo`: String, 120 caracteres, obrigatório (mínimo de 3 caracteres).
  - `Telefone`: String, 14 caracteres, obrigatório (`(XX)9XXXX-XXXX`).
  - `E-mail`: String, 200 caracteres, obrigatório, alfanumérico.
  - `Senha`: String, 30 caracteres, obrigatório.
  - `Confirmação Senha`: String, 30 caracteres, obrigatório.
  - `CEP`: Inteiro, 8 caracteres (`00000-000`), obrigatório.
  - `Logradouro`: String, 100 caracteres, obrigatório.
  - `Bairro`: String, 100 caracteres, obrigatório.
  - `Número`: Inteiro, 10 caracteres, obrigatório.
  - `Complemento`: String, 100 caracteres, opcional.
- **Regras e Validações:**
  1. O CPF deve possuir código de validação de quantidade padronizada. Se não atendida, exibe mensagem `"CPF não identificado"`, impedindo o cadastro.
  2. O nome deve conter ao menos 3 caracteres; caso contrário, exibe `"Nome muito curto"`.
  3. O telefone deve conter a quantidade exata de dígitos incluindo o DDD da região.
  4. O e-mail deve conter o caractere especial `@` seguido por `.` e texto subsequente.
  5. As senhas devem ter entre 8 e 30 caracteres. Se menor, exibe `"A senha é muito curta"`; se maior, exibe `"A senha é muito longa"`.
  6. A confirmação de senha deve ser idêntica caractere a caractere; se divergente, exibe `"As senhas são diferentes"`.
  7. O CEP deve conter exatamente 8 dígitos. Se menor, `"CEP muito curto"`; se maior, `"CEP muito longo"`.
  8. O CPF é estritamente imutável após o cadastro.
  9. Se o CEP for localizado via webservice, logradouro e bairro são autopreenchidos; caso contrário, os campos são liberados para preenchimento manual.
  10. Validação de e-mail via envio de token de 4 dígitos gerado aleatoriamente, com validade de 5 minutos.
  11. Validação de telefone via código de 4 dígitos com validade de 5 minutos.
  12. Botões: `"Cadastrar"` (com validações de campos obrigatórios e mensagens `"Campo(s) obrigatório(s) não preenchido(s)"`, `"Campo preenchido incorretamente"`, `"CPF já cadastrado"`, `"E-mail já cadastrado"`) e `"Cancelar"` (com confirmação `"Todas as alterações serão perdidas. Deseja realmente cancelar?"` com botões Sim e Não).
  13. Sucesso: redireciona para confirmação com a mensagem `"Cadastro realizado com sucesso"` e envia e-mail de confirmação.
- **Operações:**
  - *Alteração:* realizada pelo próprio cidadão ou funcionário com cargo a definir. Mantém histórico com responsável, ação, data e hora.
  - *Exclusão:* exclusão lógica com anonimização dos dados pessoais, mantendo as ocorrências registradas íntegras.
  - *Pesquisa:* busca por Nome Completo, CPF, E-mail ou Telefone.

---

### [Autenticação Cidadão.RF002]
- **Prioridade:** Essencial
- **Descrição:** Permite a autenticação segura do cidadão previamente cadastrado.
- **Campos de Entrada:**
  - `CPF`: String, obrigatório.
  - `Senha`: String, obrigatório.
- **Regras e Validações:**
  1. Validação de credenciais diretamente na base de dados.
  2. Caracteres da senha mascarados para segurança visual.
  3. Somente o CPF é aceito como identificador de login.
  4. Ao clicar em `"Entrar"`:
     - Se campos obrigatórios não preenchidos: `"Campo(s) obrigatório(s) não preenchido(s)"`.
     - Se credenciais incorretas (CPF não encontrado ou senha divergente): `"Usuário ou senha inválidos"`.
     - Se credenciais válidas: exibe confirmação e redireciona para a página inicial/painel de ocorrências.
  5. Ao clicar em `"Cancelar"`: exibe alerta `"Deseja mesmo cancelar o login? Tudo o que foi feito será apagado"`, limpando os campos e retornando à tela inicial pública.

---

### [Cadastro Funcionário.RF003]
- **Prioridade:** Essencial
- **Descrição:** Cadastro de funcionários da empresa de energia com acesso administrativo para gestão do painel de ocorrências.
- **Campos de Entrada:**
  - `CPF`: String, 14 caracteres, obrigatório (`XXX.XXX.XXX-XX`).
  - `Matrícula Funcional`: String, 20 caracteres, obrigatório.
  - `Nome completo`: String, 120 caracteres, obrigatório.
  - `Cargo`: String, 60 caracteres, obrigatório.
  - `Telefone`: String, 14 caracteres, obrigatório (`(XX)9XXXX-XXXX`).
  - `E-mail`: String, 200 caracteres, institucional, obrigatório.
  - `Senha`: String, 30 caracteres, obrigatório.
  - `Confirmar Senha`: String, 30 caracteres, obrigatório.
- **Regras e Validações:**
  1. Validação de formato de CPF com mensagem `"CPF não identificado"`.
  2. Validação de nome com mínimo de 3 caracteres (`"Nome muito curto"`).
  3. Validação de e-mail institucional com `@` e `.`.
  4. Senhas entre 8 e 30 caracteres (`"A senha é muito curta"`, `"A senha é muito longa"`) e confirmação idêntica.
  5. CPF e Matrícula Funcional são estritamente imutáveis após o cadastro.
  6. Validação de telefone com DDD.
  7. Botões `"Cadastrar"` (com validações de campos não preenchidos, `"CPF já cadastrado"`, `"E-mail já cadastrado"`) e `"Cancelar"` (com confirmação de descarte).
  8. Sucesso: exibe `"Cadastro realizado com sucesso"` e envia e-mail de confirmação.
  9. Envio de tokens de 4 dígitos (validade de 5 minutos) para validação de e-mail e telefone.
- **Operações:**
  - *Alteração:* permitida apenas por colaborador pré-registrado na base institucional com registro de log de auditoria.
  - *Exclusão:* exclusão estritamente lógica via inativação de status de acesso, preservando integridade de auditoria.
  - *Pesquisa:* busca por Nome Completo, CPF, Matrícula Funcional e E-mail.

---

### [Autenticação Funcionário.RF004]
- **Prioridade:** Essencial
- **Descrição:** Autenticação dos colaboradores para acesso à área administrativa e painel de ocorrências.
- **Campos de Entrada:**
  - `Matrícula Funcional`: String, obrigatório.
  - `Senha`: String, obrigatório (caracteres mascarados).
- **Regras e Validações:**
  1. Validação na base de colaboradores do sistema.
  2. Botões `"Entrar"` e `"Cancelar"`.
  3. Em erro de credenciais: `"Matrícula/E-mail ou senha inválidos"`.
  4. Sucesso: redireciona o operador para o painel de gestão corporativo de ocorrências.
  5. Cancelar limpa os dados e retorna à página inicial pública.

---

### [Registro de Ocorrência.RF005]
- **Prioridade:** Essencial
- **Descrição:** Permite ao cidadão autenticado notificar falhas físicas em postes de iluminação pública.
- **Campos de Entrada:**
  - `Número do Poste`: String, 10 caracteres, obrigatório (letras e números da faixa amarela).
  - `Logradouro`: String, 100 caracteres, obrigatório.
  - `Rua`: String, 100 caracteres, obrigatório.
  - `Bairro`: String, 100 caracteres, obrigatório.
  - `Ponto de Referência`: String, 200 caracteres, obrigatório.
  - `Tipo de Defeito`: Seleção única, obrigatório (`"Poste Apagado"`, `"Luz Oscilando"`, `"Estrutura Danificada"`).
  - `Descrição do Problema`: String, 300 caracteres, opcional.
  - `Foto do Poste`: Imagem, opcional.
- **Regras e Validações:**
  1. Validação obrigatória de dados de localização e identificação do poste. Se ausentes, mensagem `"Não foi dada informações o suficiente"`.
  2. Proibido registro anônimo: o CPF do cidadão autenticado é vinculado obrigatoriamente.
  3. Foto é opcional; quando fornecida, a imagem é armazenada e seu link/caminho registrado.
  4. Data e hora do registro capturadas automaticamente pelo sistema.
  5. Validação do Número do Poste: deve conter entre 8 e 10 caracteres. Se menor que 8 ou maior que 10, exibe `"Número de identificação do poste incorreta"` e bloqueia o registro.
  6. Ao finalizar, o sistema gera automaticamente uma sequência numérica de 10 caracteres (número de protocolo) e define o status como `"Pendente"`.
  7. Envio automático de notificação por e-mail com protocolo e dados do chamado.
  8. Botões: `"Registrar Ocorrência"` (exibe `"Ocorrência registrada com sucesso! O chamado foi encaminhado para a empresa de energia."` e disponibiliza no painel) e `"Cancelar"` (com confirmação `"Todas as informações preenchidas serão perdidas. Deseja realmente cancelar?"`).

---

### [Painel de ocorrências Funcionário.RF006]
- **Prioridade:** Essencial
- **Descrição:** Visualização e gerenciamento das ocorrências reportadas em Maceió pelos funcionários autorizados.
- **Campos Apresentados:**
  - `Número do Protocolo`: String, 10 caracteres, obrigatório.
  - `Número do Poste`: String, 8 caracteres, obrigatório.
  - `CPF do cidadão`: String, 14 caracteres, obrigatório.
  - `Nome Completo do cidadão`: String, 120 caracteres, obrigatório.
  - `Logradouro`: String, 100 caracteres, obrigatório.
  - `Rua`: String, 100 caracteres, obrigatório.
  - `Bairro`: String, 100 caracteres, obrigatório.
  - `Tipo de Defeito Selecionado`: String, obrigatório.
  - `Status da Ocorrência`: String, obrigatório (`"Pendente"`, `"Em progresso"`, `"Concluído"`).
  - `Data e Hora do Registro`: Data e Hora formatadas em `DD/MM/AAAA HH:MM`.
- **Regras e Funcionamento:**
  1. Acesso restrito a colaboradores com permissão administrativa ativa.
  2. Filtro e busca rápida por Número do Poste, Bairro, Status, Nome Completo ou CPF do solicitante.
  3. Paginação com 10 ocorrências por página, ordenadas decrescentemente por data de registro (mais recentes no topo).
  4. Visualização de detalhes completos (incluindo foto) e alteração de status do chamado.
  5. Sem registros correspondentes: exibe mensagem informativa `"Nenhuma ocorrência encontrada"`.
  6. Falha no banco de dados: exibe `"Não foi possível carregar o painel de ocorrências. Tente novamente mais tarde"`.

---

### [Painel de ocorrência Cidadão.RF007]
- **Prioridade:** Essencial
- **Descrição:** Visualização do histórico e status de chamados pelo próprio cidadão autenticado.
- **Campos Apresentados:**
  - `Número do Protocolo`: Serial, obrigatório.
  - `Número do Poste`: String, 8 caracteres.
  - `Logradouro`: String, 100 caracteres, obrigatório.
  - `Rua`: String, 100 caracteres, obrigatório.
  - `Bairro`: String, 100 caracteres, obrigatório.
  - `Tipo de Defeito`: String, obrigatório.
  - `Data do Registro`: Data e Hora em `DD/MM/AAAA HH:MM`.
  - `Status Atual da Ocorrência`: String (`"Pendente"`, `"Em progresso"`, `"Concluído"`).
- **Regras e Funcionamento:**
  1. Filtro automático estritamente restrito ao CPF do cidadão logado (isolamento de chamados de terceiros).
  2. Paginação em 10 itens por página, ordenados pela data de registro mais recente.
  3. Opção de visualização detalhada do chamado no card/linha.
  4. Se não houver chamados: `"Nenhuma ocorrência registrada no momento"`.
  5. Falha de comunicação com o banco: `"Não foi possível carregar o seu histórico de ocorrências. Tente novamente mais tarde"`.

---

## 5. Requisitos Não Funcionais

| ID | Categoria | Descrição | Prioridade |
|---|---|---|---|
| **[RNF01]** | Usabilidade | Interface intuitiva com orientações claras sobre como localizar o número na faixa amarela do poste e o endereço, destacando mensagens de erro por campo. | Importante |
| **[RNF02]** | Abrangência Geográfica | Operação e processamento de chamados restritos exclusivamente aos limites territoriais do município de Maceió. | Essencial |
| **[RNF03]** | Privacidade de Dados | Proteção de dados pessoais (CPF, senhas, telefone, endereço) com criptografia irreversível de senhas e proteção visual na digitação. | Essencial |
| **[RNF04]** | Plataforma e Acesso | Compatibilidade com principais navegadores e interface web/mobile responsiva para smartphones, viabilizando registro ágil em campo. | Essencial |
| **[RNF05]** | Tempo de Reação | Processamento e retorno das requisições e carregamento de painéis com latência máxima de 2 segundos em condições normais. | Essencial |

---

## 6. Requisitos de Segurança

| ID | Perigo | Solução |
|---|---|---|
| **[RS001]** | Senhas vazadas de fácil visualização | Todas as senhas devem ser armazenadas em formato não-visível com hash criptográfico seguro e mascaramento visual em tela. |

---

## 7. Matriz de Avaliação de Risco

| Severidade / Probabilidade | Catastrófico (1) | Crítico (2) | Marginal (3) | Insignificante (4) |
|---|---|---|---|---|
| **Frequente (A)** | | | | |
| **Provável (B)** | | | | |
| **Ocasional (C)** | RS004, RS006 | RS001 | | |
| **Remoto (D)** | RS003 | RS009 | | RS005 |
| **Improvável (E)** | RS002 | | | |
| **Eliminado (F)** | | | | |

---

## 8. Matriz de Rastreabilidade

Relações de dependência (`D`) e referência (`R`) entre requisitos:

| ID Requisito | RF001 | RF002 | RF003 | RF004 | RF005 | RF006 | RF007 | RF008 | RF009 | RF010 | RF011 | RF012 | RF013 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **RF001** | | R | | D | | D | D | R | D | | | D | D |
| **RF002** | R | | | | | | | | | | | | |
| **RF003** | | | | R | | D | | D | | | | | |
| **RF004** | D | | R | | R | D | D | | D | D | D | R | R |
| **RF005** | | | | R | | D | | | | | R | | |
| **RF006** | D | | D | D | | | | D | D | R | R | R | R |
| **RF007** | D | | D | | D | | | | D | R | R | D | D |
| **RF008** | R | | | D | | D | | | | | | | |
| **RF009** | D | | | D | | D | D | | | R | | D | D |

---

## 9. Análise por Pontos de Função (Contagem Indicativa)

Classificação por tipo de função e componentes fundamentais:
- **Funções do Tipo Dado:** Arquivo Lógico Interno (ALI) e Arquivo de Interface Externa (AIE).
- **Funções do Tipo Transação:** Entrada Externa (EE), Saída Externa (SE) e Consulta Externa (CE).

### Resumo por Requisito Funcional Inicial:
| Requisito Funcional | Complexidade | ALI | AIE | SE | EE | CE | Total de Pontos de Função |
|---|---|---|---|---|---|---|---|
| **RF001 (Cadastro Cidadão)** | ALTA | 15 | 10 | 7 | 6 | 6 | **44** |
| **RF002 (Autenticação Cidadão)** | MÉDIA | 10 | 7 | 5 | 4 | 4 | **30** |
| **RF003 (Cadastro Funcionário)** | BAIXA | 7 | 0 | 4 | 0 | 3 | **14** |

---

## 10. Critérios de Conclusão e Homologação

1. **Cidadão:** Realiza cadastro validando CPF, CEP e tokens de verificação de 4 dígitos em 5 minutos; autentica-se e acessa o painel de acompanhamento com seus próprios chamados.
2. **Registro de Ocorrência:** Envio com validação de número de poste (8 a 10 dígitos na faixa amarela), localização em Maceió, tipo de defeito e geração de protocolo de 10 dígitos com envio de e-mail confirmatório.
3. **Funcionário:** Autentica-se com matrícula funcional, pesquisa chamados paginados a 10 itens por página com filtros, acessa detalhes e atualiza status entre "Pendente", "Em progresso" e "Concluído".
4. **Ciclo de Vida:** Exclusão de cidadão executa anonimização lógica mantendo histórico de ocorrências; exclusão de funcionário inativa o acesso sem exclusão física.
5. **Qualidade:** Cobertura automatizada de testes cobrindo todas as validações, fluxos alternativos e mensagens literais de erro e sucesso.
