# Spec 0001: Fundação do projeto

- **Status:** Implementado
- **Requisitos:** RNF01, RNF03, RNF04 e RS001 do [PRD 0001](../prd/0001-maisluz.md)
- **Decisões:** [ADR 0001](../adr/0001-mvt-com-camada-de-service.md), [ADR 0002](../adr/0002-modelo-de-usuario-customizado.md), [ADR 0004](../adr/0004-postgresql-como-banco-de-dados.md)

Esta especificação deve ser implementada primeiro, e o modelo de usuário precisa existir antes do primeiro `migrate`.

## Configurações (`core/settings.py`)

| Configuração | Valor |
|---|---|
| `INSTALLED_APPS` | Adicionar `"contas"` e `"ocorrencias"` |
| `DATABASES` | Configurado para PostgreSQL via variáveis de ambiente (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) |
| `SECRET_KEY` | Variável de ambiente `DJANGO_SECRET_KEY`. Sem ela, usa chave temporária com `DEBUG = True` |
| `AUTH_USER_MODEL` | `"contas.Usuario"` |
| `AUTHENTICATION_BACKENDS` | `["contas.backends.CPFEmailBackend", "django.contrib.auth.backends.ModelBackend"]` |
| `LOGIN_URL` | `"contas:entrar"` |
| `LANGUAGE_CODE` | `"pt-br"` |
| `TIME_ZONE` | `"America/Maceio"` |
| `TEMPLATES[0]["DIRS"]` | `[BASE_DIR / "templates"]` |
| `STATICFILES_DIRS` | `[BASE_DIR / "static"]` |

## Estrutura

```text
core/
  settings.py
  urls.py
  views.py
contas/
  models/
    usuario.py
    auditoria.py
    solicitacao_senha.py
  forms/
    login.py
    cidadao.py
  services/
    cidadao.py
    funcionario.py
    auditoria.py
  views/
    entrar.py
    sair.py
  backends.py
  exceptions.py
  templates/contas/
  tests/
  urls.py
ocorrencias/
  models.py
  forms/
    ocorrencia.py
  services/
    ocorrencia.py
  exceptions.py
  templates/ocorrencias/
  tests/
templates/
  base_publico.html
  base_interno.html
  paginas/
  cidadao/
  ocorrencias/
  funcionarios/
static/
  css/
  js/
    viacep.js
```

Cada pacote `models/`, `views/`, `services/` e `forms/` reexporta suas classes públicas no `__init__.py`.

## Layouts base (`templates/base_publico.html` e `templates/base_interno.html`)

Todas as páginas herdam destes templates acessíveis (WCAG 2.1 AA), contendo:

- `<html lang="pt-br">` e a meta tag `viewport`
- Cabeçalhos modulares com navegação acessível e indicador de skip link
- Área de mensagens do framework `django.contrib.messages`
- Blocos `title`, `extra_css`, `content` e `extra_js`

## URLs do projeto (`core/urls.py`)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", LandingPageView.as_view(), name="inicio"),
    path("ocorrencias/registrar/", RegistrarOcorrenciaView.as_view(), name="registrar_ocorrencia"),
    path("ocorrencias/painel/", PainelOcorrenciasView.as_view(), name="ocorrencias_painel"),
    path("ocorrencias/minhas/", MinhasOcorrenciasView.as_view(), name="minhas_ocorrencias"),
    path("cidadao/cadastro/", CadastroCidadaoView.as_view(), name="cadastro_cidadao"),
    path("cidadao/perfil/", MeuPerfilCidadaoView.as_view(), name="meu_perfil_cidadao"),
    path("", include("contas.urls")),
]
```

## Critérios de aceite

- [x] `python manage.py check` não reporta problemas.
- [x] `python manage.py migrate` executa no banco PostgreSQL `maisluz` usando `contas.Usuario`.
- [x] Suíte de testes automatizados passa com 100% de sucesso.
