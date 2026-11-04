# Spec 0002: Autenticação

- **Status:** Implementado
- **Requisitos:** RF-05 e RF-15 do [PRD 0001](../prd/0001-blog.md)
- **Decisão:** [ADR 0002](../adr/0002-modelo-de-usuario-customizado.md)
- **Depende de:** [Spec 0001](0001-fundacao.md)

## Modelo

```python
class Usuario(AbstractUser):
    pass
```

O modelo é registrado no Admin com `UserAdmin`, onde o administrador cria contas e as desativa com `is_active`.

## Rotas (`app_name = "contas"`)

| Rota | Nome | View | Métodos | Acesso |
|---|---|---|---|---|
| `/entrar/` | `contas:entrar` | `EntrarView` | GET, POST | Público |
| `/sair/` | `contas:sair` | `SairView` | POST | Autenticado |

## Comportamento

### `EntrarView`

- **GET:** exibe o `AuthenticationForm`. Quem já está autenticado é redirecionado para `posts:painel`.
- **POST válido:** chama `login(request, form.get_user())` e redireciona para `next`, se for seguro, ou para `posts:painel`.
- **POST inválido:** exibe o formulário novamente com a mensagem de erro padrão, sem revelar se o usuário existe.
- O `next` é validado com `url_has_allowed_host_and_scheme`, aceitando apenas o host da requisição. O valor é repassado do GET para o POST em um campo oculto.

### `SairView`

- **POST:** chama `logout(request)` e redireciona para `posts:lista`.
- **GET:** retorna 405, pois a view não implementa `get`.

## Testes

- [x] Login com credenciais válidas redireciona para o painel.
- [x] Login com senha errada não cria sessão e mostra erro.
- [x] Conta com `is_active=False` não consegue entrar.
- [x] `next` interno é respeitado.
- [x] `next` externo, como `https://exemplo.com`, é ignorado.
- [x] Usuário autenticado que acessa `/entrar/` é redirecionado para o painel.
- [x] POST em `/sair/` encerra a sessão, e GET retorna 405.
