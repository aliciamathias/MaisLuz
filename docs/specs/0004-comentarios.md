# Spec 0004: Comentários

- **Status:** Implementado
- **Requisitos:** RF-12 a RF-14 do [PRD 0001](../prd/0001-blog.md)
- **Depende de:** [Spec 0003](0003-posts.md)

## Modelo `Comentario`

| Campo | Tipo | Regras |
|---|---|---|
| `post` | `ForeignKey(Post, on_delete=CASCADE, related_name="comentarios")` | Obrigatório |
| `nome` | `CharField(max_length=80)` | Obrigatório |
| `texto` | `TextField(max_length=2000)` | Obrigatório |
| `aprovado` | `BooleanField(default=False)` | |
| `criado_em` | `DateTimeField(auto_now_add=True)` | |

O `Meta` define índice em `(post, aprovado, criado_em)`. O `__str__` retorna o nome e o título do post.

O e-mail de quem comenta não é coletado, porque nenhuma funcionalidade desta versão o utiliza.

## `ComentarioService`

| Método | Regra |
|---|---|
| `listar_aprovados(post)` | Retorna os comentários aprovados, do mais antigo para o mais recente |
| `criar(slug, nome, texto)` | Cria um comentário pendente em um post publicado. Levanta `PostNaoEncontrado` se o post não estiver publicado |
| `aprovar(comentario_ids)` | Marca os comentários informados como aprovados e retorna a quantidade alterada |

## Form

`ComentarioForm` é um `ModelForm` com os campos `nome` e `texto`. Como o limite de um `TextField` só é aplicado pelo formulário, o campo `texto` precisa ser validado por ele.

## Rota

| Rota | Nome | View | Método | Acesso |
|---|---|---|---|---|
| `/posts/<slug:slug>/comentarios/` | `posts:comentar` | `ComentarioCreateView` | POST | Público |

## Fluxo

1. `PostDetailView` mostra o post, os comentários aprovados e o `ComentarioForm`.
2. O formulário envia um POST para `posts:comentar`.
3. Se for válido, a view chama `ComentarioService.criar`, adiciona a mensagem "Comentário enviado. Ele aparecerá após a moderação." e redireciona para o detalhe do post.
4. Se for inválido, a view obtém o post e os comentários e renderiza `posts/detalhe.html` novamente com os erros, mantendo o texto digitado.
5. Se o post não existir ou não estiver publicado, a view responde 404.

O texto é exibido com autoescape e `linebreaks`, sem `safe`.

## Admin

`ComentarioAdmin` serve para moderação:

- A listagem mostra nome, post, início do texto, `aprovado` e `criado_em`, com filtro por `aprovado` e `select_related("post")`.
- A ação "Aprovar selecionados" chama `ComentarioService.aprovar`.
- A exclusão padrão do Admin continua disponível.
- Não é possível adicionar comentários, e os campos não são editáveis, para que o texto de quem comentou não seja alterado.

## Testes

- [x] Um comentário válido é criado como pendente.
- [x] Um comentário pendente não aparece no detalhe do post.
- [x] Um comentário aprovado aparece no detalhe do post.
- [x] Comentar em rascunho ou em slug inexistente retorna 404.
- [x] Um POST inválido não cria comentário e mostra os erros.
- [x] Texto acima de 2000 caracteres é rejeitado.
- [x] GET na rota de comentar retorna 405.
- [x] Comentário com `<script>` aparece escapado.
- [x] A ação do Admin aprova os comentários selecionados.
- [x] Excluir um post exclui seus comentários.
