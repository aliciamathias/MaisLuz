# Spec 0005: Publicações iniciais

- **Status:** Implementado
- **Depende de:** [Spec 0003](0003-posts.md)

O comando abaixo cria e publica os textos de `posts/publicacoes_iniciais.py`, para que o blog não comece vazio:

```bash
python manage.py criar_publicacoes_iniciais --autor admin
```

- `--autor` é opcional, e o valor padrão é `admin`. O usuário precisa existir: caso contrário, o comando falha sem criar posts.
- A gravação é feita por `PublicacaoInicialService.criar_publicacoes`, que usa o `PostService`.
- Uma publicação cujo título já existe é ignorada, portanto o comando pode ser executado novamente.
- Não se usa migração de dados, para que os textos não apareçam no banco de testes nem dependam de um usuário existente.
