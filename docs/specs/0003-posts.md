# Spec 0003: Posts

- **Status:** Implementado
- **Requisitos:** RF-01 a RF-11 do [PRD 0001](../prd/0001-blog.md)
- **Decisões:** [ADR 0001](../adr/0001-mvt-com-camada-de-service.md), [ADR 0003](../adr/0003-conteudo-em-texto-puro.md)
- **Depende de:** [Spec 0001](0001-fundacao.md), [Spec 0002](0002-autenticacao.md)

## Modelo `Post`

| Campo | Tipo | Regras |
|---|---|---|
| `titulo` | `CharField(max_length=200)` | Obrigatório |
| `slug` | `SlugField(max_length=220, unique=True)` | Gerado pelo service e imutável |
| `conteudo` | `TextField` | Obrigatório, texto puro |
| `autor` | `ForeignKey(settings.AUTH_USER_MODEL, on_delete=PROTECT, related_name="posts")` | Obrigatório |
| `status` | `CharField` com `TextChoices` | `RASCUNHO` (padrão) ou `PUBLICADO` |
| `publicado_em` | `DateTimeField(null=True, blank=True)` | Preenchido na primeira publicação |
| `criado_em` | `DateTimeField(auto_now_add=True)` | |
| `atualizado_em` | `DateTimeField(auto_now=True)` | |

No `Meta`:

- `CheckConstraint`: um post com status `PUBLICADO` precisa ter `publicado_em`.
- Índice em `(status, -publicado_em)` para a listagem pública.

O `__str__` retorna o título.

## Exceções (`posts/exceptions.py`)

- `PostNaoEncontrado`: o post não existe, não está publicado ou pertence a outro autor, conforme a operação.

## `PostService`

| Método | Regra |
|---|---|
| `listar_publicados(pagina=1)` | Retorna uma página (`Page`) com 10 posts publicados, ordenados por `-publicado_em`, com `select_related("autor")` |
| `obter_publicado(slug)` | Retorna o post publicado ou levanta `PostNaoEncontrado` |
| `listar_do_autor(autor, pagina=1)` | Retorna uma página com 10 posts do autor, ordenados por `-criado_em` |
| `obter_do_autor(post_id, autor)` | Retorna o post do autor ou levanta `PostNaoEncontrado` |
| `criar(autor, titulo, conteudo)` | Cria um rascunho e gera o slug |
| `atualizar(post_id, autor, titulo, conteudo)` | Atualiza título e conteúdo, sem alterar slug, status ou `publicado_em` |
| `publicar(post_id, autor)` | Define `PUBLICADO`. Preenche `publicado_em` só se estiver vazio. Publicar de novo não altera nada |
| `despublicar(post_id, autor)` | Define `RASCUNHO` e mantém `publicado_em` |
| `excluir(post_id, autor)` | Exclui o post e, em cascata, seus comentários |

Páginas inválidas seguem o comportamento de `Paginator.get_page`: um valor não numérico retorna a primeira página, e um valor além do limite retorna a última.

### Geração do slug

1. Aplicar `slugify` ao título, que remove acentos e caracteres especiais.
2. Se o resultado ficar vazio, como em um título `"!!!"`, usar `"post"`.
3. Limitar a base a 200 caracteres.
4. Se o slug já existir, acrescentar `-2`, `-3` e assim por diante.

Duas criações simultâneas com o mesmo título podem gerar `IntegrityError`. O `unique=True` impede o dado duplicado, e esse caso raro é aceitável nesta versão.

## Form

`PostForm` é um `ModelForm` com os campos `titulo` e `conteudo`. Ele apenas valida. A gravação é feita pelo service, e `form.save()` não é chamado.

## Rotas (`app_name = "posts"`)

| Rota | Nome | View | Métodos | Acesso |
|---|---|---|---|---|
| `/` | `posts:lista` | `PostListView` | GET | Público |
| `/posts/<slug:slug>/` | `posts:detalhe` | `PostDetailView` | GET | Público |
| `/painel/` | `posts:painel` | `PainelView` | GET | Autor |
| `/painel/posts/novo/` | `posts:criar` | `PostCreateView` | GET, POST | Autor |
| `/painel/posts/<int:post_id>/editar/` | `posts:editar` | `PostUpdateView` | GET, POST | Dono |
| `/painel/posts/<int:post_id>/excluir/` | `posts:excluir` | `PostDeleteView` | GET, POST | Dono |
| `/painel/posts/<int:post_id>/publicar/` | `posts:publicar` | `PostPublicarView` | POST | Dono |
| `/painel/posts/<int:post_id>/despublicar/` | `posts:despublicar` | `PostDespublicarView` | POST | Dono |

As rotas do painel usam `LoginRequiredMixin`. Quando `PostNaoEncontrado` é levantada, a view responde 404. Assim, um autor não descobre se um post de outro autor existe.

As páginas de posts usam `posts/lista.html`, `posts/detalhe.html`, `posts/painel.html`, `posts/form.html` e `posts/confirmar_exclusao.html`. A listagem mostra o trecho com `truncatewords`, e o detalhe mostra o conteúdo com `linebreaks`, sem `safe`.

## Exemplo de view

```python
class PostPublicarView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        try:
            PostService.publicar(post_id, request.user)
        except PostNaoEncontrado as exc:
            raise Http404 from exc
        messages.success(request, "Post publicado.")
        return redirect("posts:painel")
```

## Admin

`Post` é somente leitura no Admin (`has_add_permission`, `has_change_permission` e `has_delete_permission` retornam `False`), pois gravar por lá ignoraria o `PostService`.

## Testes

### Service

- [x] `criar` gera rascunho com o slug esperado, incluindo título acentuado.
- [x] Títulos iguais geram slugs diferentes.
- [x] Título sem caracteres válidos gera slug com base `post`.
- [x] `atualizar` não altera o slug.
- [x] `publicar` preenche `publicado_em`, e uma nova publicação mantém a data.
- [x] `despublicar` volta para rascunho e tira o post da listagem pública.
- [x] Operações com o post de outro autor levantam `PostNaoEncontrado`.
- [x] `listar_publicados` ignora rascunhos, ordena corretamente e pagina de 10 em 10.
- [x] `listar_publicados` não faz uma consulta extra por autor (`assertNumQueries`).

### Views

- [x] A página inicial e o detalhe de um post publicado retornam 200.
- [x] O detalhe de um rascunho retorna 404, inclusive para o próprio autor.
- [x] Rotas do painel redirecionam visitantes para o login.
- [x] Rotas do painel retornam 404 para posts de outro autor.
- [x] GET em `publicar` e `despublicar` retorna 405.
- [x] GET em `excluir` não exclui, e POST exclui.
- [x] Conteúdo com `<script>` aparece escapado no detalhe.
