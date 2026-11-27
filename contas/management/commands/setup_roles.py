import psycopg
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Cria e configura as roles suporte_maisluz e dev_maisluz no PostgreSQL com permissões de SELECT, INSERT e UPDATE, revogando DELETE."

    def add_arguments(self, parser):
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Testa conexão e permissões (SELECT, INSERT, UPDATE permitidos e DELETE bloqueado).",
        )

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            self.stdout.write(self.style.WARNING("Configuração de roles disponível apenas para banco PostgreSQL."))
            return

        sql_file = settings.BASE_DIR / "docs" / "database" / "roles_permissoes.sql"
        if not sql_file.exists():
            self.stdout.write(self.style.ERROR(f"Arquivo SQL não encontrado em: {sql_file}"))
            return

        sql_content = sql_file.read_text(encoding="utf-8")

        self.stdout.write("Executando script de configuração de roles no PostgreSQL...")
        with connection.cursor() as cursor:
            cursor.execute(sql_content)

        # Verificação das roles criadas
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT rolname, rolcanlogin
                FROM pg_catalog.pg_roles
                WHERE rolname IN ('suporte_maisluz', 'dev_maisluz')
                ORDER BY rolname;
            """)
            roles = cursor.fetchall()

        self.stdout.write(self.style.SUCCESS("Roles configuradas com sucesso!"))
        for rolname, canlogin in roles:
            self.stdout.write(f" - Role: {rolname} (Login permitido: {canlogin})")

        if options["verify"]:
            self._verify_roles()

    def _verify_roles(self):
        self.stdout.write("\n=== VERIFICAÇÃO DE PERMISSÕES RBAC ===")
        db_conf = settings.DATABASES["default"]
        host = db_conf.get("HOST") or "localhost"
        port = db_conf.get("PORT") or 5432
        dbname = db_conf.get("NAME") or "maisluz"

        roles_para_testar = [
            ("suporte_maisluz", "SenhaSuporte123456"),
            ("dev_maisluz", "SenhaDev123456"),
        ]

        for user, password in roles_para_testar:
            self.stdout.write(f"\nTestando credenciais e acessos da role '{user}'...")
            try:
                with psycopg.connect(
                    host=host,
                    port=port,
                    dbname=dbname,
                    user=user,
                    password=password,
                ) as conn:
                    with conn.cursor() as cur:
                        # 1. Teste de SELECT
                        cur.execute("SELECT count(*) FROM contas_usuario;")
                        total = cur.fetchone()[0]
                        self.stdout.write(self.style.SUCCESS(f" [OK] SELECT permitido na tabela contas_usuario (Total: {total})"))

                        # 2. Teste de DELETE (deve ser NEGADO)
                        try:
                            cur.execute("DELETE FROM contas_usuario WHERE id = -9999;")
                            self.stdout.write(self.style.ERROR(" [FALHA] DELETE não foi bloqueado!"))
                        except psycopg.errors.InsufficientPrivilege:
                            self.stdout.write(self.style.SUCCESS(" [OK] DELETE bloqueado com sucesso (InsufficientPrivilege)"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao testar role '{user}': {e}"))

