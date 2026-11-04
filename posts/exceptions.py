class PostNaoEncontrado(Exception):
    """O post não existe, não está publicado ou pertence a outro autor."""


class AutorNaoEncontrado(Exception):
    """Não existe usuário com o nome informado."""
