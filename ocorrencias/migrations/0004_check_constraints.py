from django.db import migrations


def apply_check_constraints(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                ALTER TABLE contas_usuario
                DROP CONSTRAINT IF EXISTS chk_usuario_nome_completo_min_length;

                ALTER TABLE contas_usuario
                ADD CONSTRAINT chk_usuario_nome_completo_min_length
                CHECK (
                    is_superuser = TRUE
                    OR tipo_perfil NOT IN ('CIDADAO', 'FUNCIONARIO')
                    OR trim(nome_completo) = ''
                    OR char_length(trim(nome_completo)) >= 3
                );

                ALTER TABLE ocorrencias_ocorrencia
                DROP CONSTRAINT IF EXISTS chk_ocorrencia_status_valido;

                ALTER TABLE ocorrencias_ocorrencia
                ADD CONSTRAINT chk_ocorrencia_status_valido
                CHECK (
                    status IN (
                        'Pendente', 'pendente',
                        'Em progresso', 'em progresso',
                        'Concluído', 'concluído', 'Concluido', 'concluido',
                        'Excluído', 'excluído', 'Excluido', 'excluido',
                        'Excluído pelo Cidadão', 'Excluído pelo Funcionário'
                    )
                );

                CREATE OR REPLACE VIEW ocorrencias_ocorrencias AS
                SELECT * FROM ocorrencias_ocorrencia;
            """)
        else:
            # Compatibilidade com SQLite
            cursor.execute("""
                DROP VIEW IF EXISTS ocorrencias_ocorrencias;
                CREATE VIEW ocorrencias_ocorrencias AS
                SELECT * FROM ocorrencias_ocorrencia;
            """)


def revert_check_constraints(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                ALTER TABLE contas_usuario
                DROP CONSTRAINT IF EXISTS chk_usuario_nome_completo_min_length;

                ALTER TABLE ocorrencias_ocorrencia
                DROP CONSTRAINT IF EXISTS chk_ocorrencia_status_valido;

                DROP VIEW IF EXISTS ocorrencias_ocorrencias;
            """)
        else:
            cursor.execute("""
                DROP VIEW IF EXISTS ocorrencias_ocorrencias;
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0003_trigger_indices_views'),
        ('contas', '0003_historicoauditoria_ocorrencia_and_more'),
    ]

    operations = [
        migrations.RunPython(apply_check_constraints, revert_check_constraints),
    ]
