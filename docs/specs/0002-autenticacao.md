# Spec 0002: Autenticação e Perfis

- **Status:** Implementado
- **Requisitos:** RF001, RF002, RF008 e RF011 do [PRD 0001](../prd/0001-maisluz.md)
- **Decisão:** [ADR 0002](../adr/0002-modelo-de-usuario-customizado.md)
- **Depende de:** [Spec 0001](0001-fundacao.md)

## Modelo `Usuario` (`contas/models/usuario.py`)

Herda de `AbstractUser` e implementa os campos e restrições específicos do MaisLuz:

| Campo | Tipo | Regras |
|---|---|---|
| `nome_completo` | `CharField(max_length=120)` | Mínimo 3 caracteres no formulário |
| `cpf` | `CharField(max_length=14, unique=True, null=True, blank=True)` | Imutável após cadastro, formato `XXX.XXX.XXX-XX` |
| `telefone` | `CharField(max_length=14)` | DDD + 9 dígitos, formato `(XX)9XXXX-XXXX` |
| `tipo_perfil` | `CharField(choices=TipoPerfil.choices)` | `CIDADAO` (padrão) ou `FUNCIONARIO` |
| `status_acesso` | `CharField(choices=StatusAcesso.choices)` | `ATIVO` (padrão), `BLOQUEADO` ou `INATIVO` |
| `anonimizado` | `BooleanField(default=False)` | Para exclusão lógica e LGPD do cidadão |
| `cep` | `CharField(max_length=8)` | 8 dígitos, busca dinâmica via ViaCEP (Maceió/AL) |
| `logradouro`, `bairro` | `CharField(max_length=100)` | Endereço do cidadão |
| `numero` | `CharField(max_length=10)` | Número predial |
| `complemento` | `CharField(max_length=100)` | Opcional |
| `matricula_funcional` | `CharField(max_length=20, unique=True, null=True, blank=True)` | Exclusivo de Funcionário, imutável |
| `cargo` | `CharField(max_length=60)` | Exclusivo de Funcionário (Administrador, Atendente, etc.) |

## Backend de Autenticação (`contas/backends.py`)

A classe `CPFEmailBackend` permite que o cidadão e o operador façam login informando:
- CPF (com ou sem pontuação)
- E-mail
- Matrícula funcional
- Username

## Rotas (`app_name = "contas"`)

| Rota | Nome | View | Métodos | Acesso |
|---|---|---|---|---|
| `/contas/entrar/` | `contas:entrar` | `EntrarView` | GET, POST | Público |
| `/contas/sair/` | `contas:sair` | `SairView` | POST | Autenticado |
| `/cidadao/cadastro/` | `cadastro_cidadao` | `CadastroCidadaoView` | GET, POST | Público (visitante) |
| `/cidadao/perfil/` | `meu_perfil_cidadao` | `MeuPerfilCidadaoView` | GET, POST | Cidadão autenticado |

## Comportamento

### `EntrarView`

- **GET:** Exibe o `LoginForm`. Se o usuário já estiver autenticado:
  - Cidadão é redirecionado para `minhas_ocorrencias`.
  - Funcionário/Admin é redirecionado para `ocorrencias_painel`.
- **POST válido:** Autentica com `login(request, user)` e redireciona para `next` seguro ou:
  - `minhas_ocorrencias` para cidadão.
  - `ocorrencias_painel` para funcionário.
- **POST inválido:** Exibe erro amigável (`"Usuário ou senha inválidos"` ou `"Campo(s) obrigatório(s) não preenchido(s)"`).
- **Cancelamento:** Modal acessível confirma antes de descartar dados.

### `SairView`

- **POST:** Encerra a sessão via `logout(request)` e redireciona para `inicio`.
- **GET:** Retorna 405 (método não permitido).

## Testes

- [x] Login com credenciais válidas redireciona para o painel correto (cidadão vs funcionário).
- [x] Login aceita CPF ou e-mail.
- [x] Senha errada não cria sessão e exibe `"Usuário ou senha inválidos"`.
- [x] Usuário inativo ou bloqueado não consegue entrar.
- [x] Parâmetro `next` seguro é respeitado.
- [x] Edição de perfil preserva CPF imutável e valida campos obrigatórios.
- [x] Cancelamento de formulário possui modal de confirmação.
