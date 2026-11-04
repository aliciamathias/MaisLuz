from django.core.management.base import BaseCommand, CommandError

from posts.exceptions import AutorNaoEncontrado
from posts.services import PublicacaoInicialService


class Command(BaseCommand):
    help = "Cria e publica as publicações iniciais do blog, ignorando as que já existem."

    def add_arguments(self, parser):
        parser.add_argument("--autor", default="admin", help="Nome de usuário do autor (padrão: admin).")

    def handle(self, *args, **options):
        try:
            quantidade = PublicacaoInicialService.criar_publicacoes(options["autor"])
        except AutorNaoEncontrado as exc:
            raise CommandError(f"Usuário não encontrado: {options['autor']}") from exc
        self.stdout.write(self.style.SUCCESS(f"Publicações criadas: {quantidade}."))
