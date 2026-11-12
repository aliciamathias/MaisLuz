# ADR 0002: Modelo de usuário customizado e autenticação própria

- **Status:** Aceito
- **Data:** 2026-11-11

## Contexto

O sistema MaisLuz ([PRD 0001](../prd/0001-maisluz.md)) necessita de autenticação e identificação de múltiplos perfis de usuários: cidadãos (identificados obrigatoriamente por CPF para coibir denúncias anônimas e trotes ao registrar ocorrências), funcionários da concessionária (identificados por matrícula funcional para gestão do painel corporativo de iluminação pública) e administradores institucionais.

A documentação oficial do Django recomenda definir um modelo de usuário customizado logo no início do desenvolvimento, pois substituir o modelo padrão após as primeiras migrações de banco de dados é um processo complexo e custoso. Como o sistema exige dados específicos para os perfis e mecanismos próprios de acesso, a adoção de um modelo customizado desde a concepção é indispensável.

Além disso, a autenticação padrão fornecida pelo Django utiliza o `LoginView`, que é uma generic view, o que contraria as diretrizes de arquitetura definidas na [ADR 0001](0001-mvt-com-camada-de-service.md).

## Decisão

- Criar o app `contas`, com o modelo `Usuario` herdando de `AbstractUser`, estruturado para suportar os dados e perfis do sistema.
- Definir `AUTH_USER_MODEL = "contas.Usuario"` antes da primeira execução de `migrate`.
- Usar o sistema de autenticação do Django: `AuthenticationForm`, `login()`, `logout()` e `LoginRequiredMixin`.
- Escrever as views de entrar e sair como classes que herdam de `View`.
- Chamar `login()` e `logout()` na view, pois eles alteram a sessão HTTP e precisam de `request`. Essa é uma exceção esperada à delegação para services.

## Consequências

- Campos de perfil (como CPF, matrícula funcional, telefone corporativo e endereços) podem ser integrados e evoluídos de forma consistente.
- O código deve referenciar o usuário por `settings.AUTH_USER_MODEL` ou `get_user_model()`, nunca importando `User` diretamente.
- Há um app a mais, e a validação segura do parâmetro `next` no login passa a ser responsabilidade do projeto.
