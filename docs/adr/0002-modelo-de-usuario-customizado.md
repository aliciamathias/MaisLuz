# ADR 0002: Modelo de usuário customizado e autenticação própria

- **Status:** Aceito
- **Data:** 2026-11-04

## Contexto

O blog precisa de contas para autores e administradores. A documentação do Django recomenda definir um modelo de usuário customizado ao iniciar um projeto, porque trocá-lo depois das primeiras migrações é trabalhoso. O projeto ainda não tem banco de dados nem migrações aplicadas, então este é o momento mais barato para decidir.

O `LoginView` do Django é uma generic view, o que a [ADR 0001](0001-mvt-com-camada-de-service.md) não permite.

## Decisão

- Criar o app `contas`, com o modelo `Usuario` herdando de `AbstractUser`, sem campos adicionais por enquanto.
- Definir `AUTH_USER_MODEL = "contas.Usuario"` antes da primeira execução de `migrate`.
- Usar o sistema de autenticação do Django: `AuthenticationForm`, `login()`, `logout()` e `LoginRequiredMixin`.
- Escrever as views de entrar e sair como classes que herdam de `View`.
- Chamar `login()` e `logout()` na view, pois eles alteram a sessão HTTP e precisam de `request`. Essa é uma exceção esperada à delegação para services.

## Consequências

- Novos campos de perfil poderão ser adicionados sem migração complexa.
- O código deve referenciar o usuário por `settings.AUTH_USER_MODEL` ou `get_user_model()`, nunca importando `User` diretamente.
- Há um app a mais, e a validação segura do parâmetro `next` no login passa a ser responsabilidade do projeto.
