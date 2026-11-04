# Spec 0001: Fundação do projeto

- **Status:** Implementado
- **Requisitos:** RNF-01, RNF-03 e RNF-04 do [PRD 0001](../prd/0001-blog.md)
- **Decisões:** [ADR 0001](../adr/0001-mvt-com-camada-de-service.md), [ADR 0002](../adr/0002-modelo-de-usuario-customizado.md)

Esta especificação deve ser implementada primeiro, e o modelo de usuário precisa existir antes do primeiro `migrate`.

## Configurações (`core/settings.py`)

| Configuração | Valor |
|---|---|
| `INSTALLED_APPS` | Adicionar `"contas"` e `"posts"` |
| `SECRET_KEY` | Variável de ambiente `DJANGO_SECRET_KEY`. Sem ela, usa uma chave temporária com `DEBUG = True`. Com `DEBUG = False`, o Django levanta erro ao precisar da chave |
| `AUTH_USER_MODEL` | `"contas.Usuario"` |
| `LOGIN_URL` | `"contas:entrar"` |
| `LANGUAGE_CODE` | `"pt-br"` |
| `TIME_ZONE` | `"America/Maceio"` |
| `TEMPLATES[0]["DIRS"]` | `[BASE_DIR / "templates"]` |
| `STATICFILES_DIRS` | `[BASE_DIR / "static"]` |

## Estrutura

```text
core/
  urls.py               # inclui posts.urls e contas.urls
contas/
  models/usuario.py
  forms/
  views/
  templates/contas/
  tests/
  urls.py
posts/
  models/
  forms/
  services/
  views/
  templates/posts/
  tests/
  exceptions.py
  urls.py
templates/base.html
static/css/site.css
```

Cada pacote `models/`, `views/`, `services/` e `forms/` reexporta suas classes públicas no `__init__.py`. O arquivo `posts/tests.py` deve ser removido ao criar o pacote `posts/tests/`, pois os dois têm o mesmo nome de módulo.

## Layout base (`templates/base.html`)

Todas as páginas herdam deste template, que contém:

- `<html lang="pt-br">` e a meta tag `viewport`
- Cabeçalho com link para a página inicial
- Para visitantes: link "Entrar"
- Para autores: link "Painel" e botão "Sair", em um formulário POST com `{% csrf_token %}`
- Área de mensagens do framework `django.contrib.messages`
- Blocos `title` e `content`

## URLs do projeto (`core/urls.py`)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("contas.urls")),
    path("", include("posts.urls")),
]
```

## Teste de arquitetura

`posts/tests/test_arquitetura.py` percorre os módulos de `contas.views` e `posts.views` e falha se:

1. uma classe definida no módulo com nome terminado em `View` não tiver `django.views.View` em `__bases__`;
2. uma função pública for usada como view em `urls.py`, ou seja, algum padrão de URL não apontar para uma view criada com `as_view()` (com exceção das rotas do Admin).

## Critérios de aceite

- [x] `python manage.py check` não reporta problemas.
- [x] `python manage.py migrate` executa em um banco novo usando `contas.Usuario`.
- [x] O teste de arquitetura passa.
