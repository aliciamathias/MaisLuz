# PRD 0001: MaisLuz

- **Status:** Proposto
- **Data:** 2026-11-11
- **Especificações:** a definir

## Objetivo

Disponibilizar uma plataforma web com abrangência geográfica estritamente delimitada ao município de Maceió, servindo como canal direto de comunicação entre os cidadãos e a concessionária de energia ou órgão público responsável pela iluminação pública. A ferramenta permite que cidadãos previamente identificados registrem ocorrências de falhas em postes e acompanhem o andamento dos chamados, enquanto colaboradores da concessionária visualizam, filtram e gerenciam os status das ocorrências em um painel centralizado.

## Perfis de uso

| Perfil | Quem é | O que precisa fazer |
|---|---|---|
| Cidadão | Morador de Maceió cadastrado com CPF | Cadastrar-se, autenticar-se, registrar ocorrências de iluminação com dados do poste e acompanhar o status dos seus chamados no painel pessoal |
| Funcionário | Colaborador da empresa de energia com matrícula funcional | Autenticar-se, consultar, filtrar, visualizar detalhes e atualizar o status das ocorrências no painel corporativo |
| Administrador | Gestor institucional da empresa de energia | Cadastrar e gerenciar contas de funcionários e auditar históricos de operações e ocorrências |

## Requisitos funcionais

### Cadastro de Cidadãos

- **RF-01:** O cidadão cadastra-se informando CPF, nome completo (mínimo de 3 caracteres), telefone com DDD, e-mail, senha (de 8 a 30 caracteres), confirmação de senha, CEP (8 dígitos), logradouro, bairro, número e complemento opcional.
- **RF-02:** O sistema valida o CPF no formato `XXX.XXX.XXX-XX`; se estiver incompleto ou inválido, impede o cadastro com a mensagem "CPF não identificado", e se já estiver em uso, exibe "CPF já cadastrado".
- **RF-03:** O CPF do cidadão torna-se imutável após a conclusão do cadastro.
- **RF-04:** O sistema valida a quantidade de caracteres do telefone com DDD e o formato do e-mail com `@`, ponto e domínio válido, impedindo o cadastro caso o e-mail já esteja cadastrado ("E-mail já cadastrado").
- **RF-05:** O sistema valida a confirmação de uso do e-mail e do telefone enviando um token de 4 dígitos gerado aleatoriamente para cada canal, exigindo a digitação exata em até 5 minutos.
- **RF-06:** O sistema exige que a senha tenha entre 8 e 30 caracteres (exibindo "A senha é muito curta" ou "A senha é muito longa") e que a confirmação seja idêntica (exibindo "As senhas são diferentes").
- **RF-07:** O sistema valida o CEP com exatamente 8 dígitos (exibindo "CEP muito curto" ou "CEP muito longo"); se localizado via serviço de busca, autoppreenche logradouro e bairro; caso contrário, permite o preenchimento manual dos campos.
- **RF-08:** O formulário de cadastro exibe os botões "Cadastrar" (validando campos obrigatórios não preenchidos e incorretos) e "Cancelar" (com diálogo de confirmação para descarte dos dados ou permanência na tela).
- **RF-09:** Após o cadastro bem-sucedido, o sistema redireciona o cidadão para uma página de confirmação com a mensagem "Cadastro realizado com sucesso" e envia um e-mail de confirmação.
- **RF-10:** O cidadão atualiza seus próprios dados cadastrais (exceto CPF), mantendo histórico de alterações com responsável, ação realizada, data e hora.
- **RF-11:** O cidadão solicita a exclusão lógica da sua conta, resultando na anonimização dos seus dados pessoais e na preservação integral das ocorrências por ele registradas.
- **RF-12:** O sistema permite a busca do cadastro de cidadãos por nome completo, CPF, e-mail ou telefone.

### Autenticação de Cidadãos

- **RF-13:** O cidadão autentica-se informando exclusivamente seu CPF e sua senha, com caracteres da senha mascarados para segurança visual.
- **RF-14:** O sistema rejeita o acesso e exibe a mensagem "Usuário ou senha inválidos" caso o CPF não seja localizado ou a senha informada seja divergente.
- **RF-15:** Ao autenticar-se com sucesso, o cidadão é redirecionado para a página inicial com seu painel de controle de ocorrências.
- **RF-16:** O botão "Cancelar" na tela de login exibe aviso de confirmação e, se aceito, limpa os campos e retorna à tela pública inicial.
- **RF-17:** O cidadão encerra sua sessão autenticada a qualquer momento, retornando à área pública.

### Cadastro de Funcionários

- **RF-18:** O funcionário é cadastrado informando CPF, matrícula funcional, nome completo (mínimo de 3 caracteres), cargo, telefone corporativo com DDD, e-mail institucional, senha (de 8 a 30 caracteres) e confirmação de senha.
- **RF-19:** O sistema valida a unicidade do CPF e da matrícula funcional, tornando ambos imutáveis após o cadastro.
- **RF-20:** O cadastro de funcionário valida e-mail e telefone mediante envio de token de 4 dígitos com validade de 5 minutos para cada canal.
- **RF-21:** O cadastro de funcionário valida comprimento de senha (8 a 30 caracteres) e igualdade na confirmação de senha.
- **RF-22:** A alteração de dados de funcionários só pode ser efetuada por colaborador com permissão administrativa pré-registrado, mantendo histórico de auditoria com autor, alteração, data e hora.
- **RF-23:** A exclusão de funcionário é tratada exclusivamente como exclusão lógica (inativação do status de acesso), sendo proibida a exclusão física para preservação de auditoria.
- **RF-24:** O sistema permite buscar funcionários por nome completo, CPF, matrícula funcional ou e-mail.

### Autenticação de Funcionários

- **RF-25:** O funcionário autentica-se na área administrativa informando sua matrícula funcional e senha mascarada.
- **RF-26:** O sistema valida o acesso na base institucional e, em caso de erro, exibe a mensagem "Matrícula/E-mail ou senha inválidos".
- **RF-27:** Ao autenticar-se com sucesso, o funcionário é redirecionado para o painel de gestão corporativo de ocorrências.
- **RF-28:** O botão "Cancelar" na tela de login administrativo limpa os campos informados e redireciona para a tela inicial pública.

### Registro de Ocorrências pelo Cidadão

- **RF-29:** O cidadão autenticado registra ocorrência informando número de identificação do poste (entre 8 e 10 caracteres, com máscara alfanumérica da faixa amarela), logradouro, rua, bairro, ponto de referência e tipo de defeito obrigatório.
- **RF-30:** O sistema valida o tamanho do identificador do poste; caso tenha menos de 8 ou mais de 10 caracteres, bloqueia o envio exibindo a mensagem "Número de identificação do poste incorreta".
- **RF-31:** O sistema oferece como opções obrigatórias de tipo de defeito: "Poste Apagado", "Luz Oscilando" e "Estrutura Danificada".
- **RF-32:** O cidadão pode adicionar opcionalmente uma descrição detalhada de até 300 caracteres e anexar uma foto do poste.
- **RF-33:** O sistema impede o registro de ocorrências anônimas, vinculando obrigatoriamente o CPF do cidadão autenticado e a data/hora exata do envio ao registro da ocorrência.
- **RF-34:** O formulário valida a presença de todos os campos obrigatórios de identificação e localização física, exibindo "Não foi dada informações o suficiente" ou "Campos obrigatórios não preenchidos" com destaque visual caso faltem dados.
- **RF-35:** Ao submeter a ocorrência com sucesso, o sistema gera um protocolo numérico de 10 dígitos, define o status inicial como "Pendente" e disponibiliza o chamado instantaneamente no painel corporativo.
- **RF-36:** Após o registro bem-sucedido, o sistema exibe a mensagem "Ocorrência registrada com sucesso! O chamado foi encaminhado para a empresa de energia." e envia um e-mail de notificação ao cidadão com o protocolo e os dados do chamado.
- **RF-37:** O botão "Cancelar" no formulário de ocorrência exige confirmação antes de descartar os dados e retornar à tela inicial.

### Painel de Ocorrências do Cidadão

- **RF-38:** O cidadão autenticado visualiza em seu painel apenas os chamados associados ao seu próprio CPF, garantindo que não veja dados de outros usuários.
- **RF-39:** A listagem do cidadão apresenta número de protocolo, número do poste, endereço (logradouro, rua, bairro), tipo de defeito, data/hora do registro (`DD/MM/AAAA HH:MM`) e status atual da ocorrência.
- **RF-40:** O painel do cidadão exibe 10 ocorrências por página, ordenadas por padrão da mais recente para a mais antiga.
- **RF-41:** O cidadão acessa a visualização detalhada de um chamado específico a partir da sua listagem.
- **RF-42:** Quando o cidadão não possuir chamados cadastrados, o painel exibe a mensagem informativa "Nenhuma ocorrência registrada no momento".
- **RF-43:** Em caso de indisponibilidade ou falha de conexão com a base de dados, o painel do cidadão exibe a mensagem "Não foi possível carregar o seu histórico de ocorrências. Tente novamente mais tarde".

### Gestão Corporativa de Ocorrências pelo Funcionário

- **RF-44:** O funcionário autenticado visualiza no painel corporativo todos os chamados reportados no município de Maceió, paginados em 10 itens por página e ordenados decrescentemente por data de registro.
- **RF-45:** A listagem corporativa exibe protocolo, número do poste, CPF e nome completo do cidadão, endereço completo, tipo de defeito, data/hora do registro (`DD/MM/AAAA HH:MM`) e status do chamado.
- **RF-46:** O painel corporativo disponibiliza campos de filtro e busca rápida por número do poste, bairro, status do chamado, nome completo ou CPF do solicitante.
- **RF-47:** O funcionário visualiza os detalhes completos da ocorrência selecionada (incluindo foto anexada, quando existente) e atualiza seu status entre "Pendente", "Em progresso" e "Concluído".
- **RF-48:** Quando a consulta ou filtros não retornarem chamados, o painel exibe a mensagem "Nenhuma ocorrência encontrada".
- **RF-49:** Em caso de falha de comunicação com a base de dados no painel corporativo, o sistema exibe a mensagem "Não foi possível carregar o painel de ocorrências. Tente novamente mais tarde".

## Requisitos não funcionais

- **RNF-01 (arquitetura):** O sistema adota o padrão MVT com separação estrita da lógica de negócio e consultas ao ORM na camada de services, conforme [`docs/arquitetura.md`](../arquitetura.md).
- **RNF-02 (abrangência geográfica):** O sistema restringe o cadastro e processamento de ocorrências exclusivamente ao território do município de Maceió.
- **RNF-03 (segurança e criptografia):** As senhas de cidadãos e colaboradores são armazenadas criptografadas com hash irreversível, nunca visíveis em texto plano, e os campos de senha na interface utilizam máscara de proteção visual.
- **RNF-04 (proteção de dados e privacidade):** Dados pessoais e sensíveis (CPF, telefone, endereços) são resguardados contra visualização não autorizada, com isolamento estrito entre usuários e mecanismo de anonimização no descarte de contas.
- **RNF-05 (usabilidade e clareza):** A interface fornece orientações claras para identificação da numeração da faixa amarela dos postes e exibe mensagens de erro explicativas e demarcadas para cada validação não atendida.
- **RNF-06 (plataforma e responsividade):** A interface web é compatível com os principais navegadores modernos e adaptável a dispositivos móveis (smartphones), permitindo o registro ágil de ocorrências em campo.
- **RNF-07 (desempenho e latência):** O sistema processa e responde a requisições de submissão de chamados e carregamento de painéis em no máximo 2 segundos em condições normais de uso.
- **RNF-08 (auditoria e integridade):** A exclusão física de registros de usuários com histórico de ocorrências ou ações operacionais é proibida, garantindo rastreabilidade por meio de inativação ou anonimização com log de data/hora e autor.
- **RNF-09 (qualidade):** Cada requisito funcional conta com pelo menos um teste automatizado correspondente na suíte de testes.

## Fora do escopo desta versão

- Gestão interna, roteirização ou despacho de equipes de manutenção em campo da concessionária
- Controle de suprimentos, materiais, peças de reposição e ordens de serviço internas da empresa de energia
- Registro e acompanhamento de ocorrências fora dos limites geográficos do município de Maceió
- Denúncias anônimas ou abertura de chamados sem autenticação prévia por CPF
- Integração bidirecional direta com sistemas de ERP, despacho ou telemetria legados da concessionária
- Aplicativos nativos instaláveis (iOS e Android), sendo a experiência móvel provida via web responsiva
- Notificações por canais além de e-mail (como SMS ou push notifications nativos)

## Critérios de conclusão

1. O cidadão realiza o cadastro completo, valida os tokens de e-mail e telefone, autentica-se e acessa seu painel pessoal.
2. O cidadão autenticado registra uma ocorrência informando a identificação do poste e localização em Maceió, anexa foto/descrição opcional, recebe o protocolo de 10 dígitos e o e-mail de confirmação.
3. O cidadão acompanha o histórico e o status atualizado ("Pendente", "Em progresso", "Concluído") de suas próprias ocorrências no painel pessoal, sem acesso aos dados de terceiros.
4. O funcionário autentica-se com sua matrícula funcional, pesquisa/filtra ocorrências no painel corporativo e atualiza o status de atendimento de um chamado.
5. A exclusão de contas de cidadãos executa a anonimização lógica mantendo os chamados íntegros, e a exclusão de funcionários realiza a inativação de acesso.
6. Todos os requisitos funcionais possuem testes automatizados cobrindo fluxos de sucesso e exceções de validação, e a suíte completa passa sem erros.

