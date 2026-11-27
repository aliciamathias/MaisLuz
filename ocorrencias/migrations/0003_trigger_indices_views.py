from django.db import migrations


def apply_custom_db_objects(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_ocorrencias (
                    id BIGSERIAL PRIMARY KEY,
                    ocorrencia_id BIGINT NOT NULL,
                    status_anterior VARCHAR(50),
                    status_novo VARCHAR(50) NOT NULL,
                    data_alteracao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_historico_ocorrencias_ocorrencia
                        FOREIGN KEY (ocorrencia_id)
                        REFERENCES ocorrencias_ocorrencia (id)
                        ON DELETE CASCADE
                );

                CREATE OR REPLACE FUNCTION fn_trg_historico_ocorrencias()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF (OLD.status IS DISTINCT FROM NEW.status) THEN
                        INSERT INTO historico_ocorrencias (
                            ocorrencia_id,
                            status_anterior,
                            status_novo,
                            data_alteracao
                        ) VALUES (
                            NEW.id,
                            OLD.status,
                            NEW.status,
                            CURRENT_TIMESTAMP
                        );
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                DROP TRIGGER IF EXISTS trg_historico_ocorrencias_status ON ocorrencias_ocorrencia;

                CREATE TRIGGER trg_historico_ocorrencias_status
                AFTER UPDATE ON ocorrencias_ocorrencia
                FOR EACH ROW
                WHEN (OLD.status IS DISTINCT FROM NEW.status)
                EXECUTE FUNCTION fn_trg_historico_ocorrencias();

                -- Índices em campos que não possuem PK ou UNIQUE
                CREATE INDEX IF NOT EXISTS idx_contas_usuario_email ON contas_usuario (email);
                CREATE INDEX IF NOT EXISTS idx_cidadao_email ON contas_usuario (email) WHERE tipo_perfil = 'CIDADAO';
                CREATE INDEX IF NOT EXISTS idx_funcionario_email ON contas_usuario (email) WHERE tipo_perfil = 'FUNCIONARIO';

                CREATE INDEX IF NOT EXISTS idx_ocorrencias_status ON ocorrencias_ocorrencia (status);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_bairro ON ocorrencias_ocorrencia (bairro);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_numero_poste ON ocorrencias_ocorrencia (numero_poste);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_data_registro ON ocorrencias_ocorrencia (data_registro);

                -- Views auxiliares
                CREATE OR REPLACE VIEW ocorrencias AS
                SELECT * FROM ocorrencias_ocorrencia;

                CREATE OR REPLACE VIEW cidadao AS
                SELECT * FROM contas_usuario WHERE tipo_perfil = 'CIDADAO';

                CREATE OR REPLACE VIEW funcionarios AS
                SELECT * FROM contas_usuario WHERE tipo_perfil = 'FUNCIONARIO';

                -- View principal do painel de ocorrências ativas
                CREATE OR REPLACE VIEW vw_painel_ocorrencias_ativas AS
                SELECT
                    o.id,
                    o.protocolo,
                    o.numero_poste,
                    o.logradouro,
                    o.rua,
                    o.bairro,
                    o.ponto_referencia,
                    o.tipo_defeito,
                    o.status,
                    o.data_registro,
                    o.cidadao_id,
                    COALESCE(NULLIF(u.nome_completo, ''), o.nome_cidadao_snapshot, u.username) AS nome_completo,
                    COALESCE(NULLIF(u.cpf, ''), o.cpf_cidadao_snapshot) AS cpf
                FROM ocorrencias_ocorrencia o
                LEFT JOIN contas_usuario u ON o.cidadao_id = u.id
                WHERE o.status IN ('Pendente', 'Em progresso');
            """)
        else:
            # Compatibilidade com SQLite (usado em testes automatizados locais)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_ocorrencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ocorrencia_id INTEGER NOT NULL,
                    status_anterior TEXT,
                    status_novo TEXT NOT NULL,
                    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ocorrencia_id) REFERENCES ocorrencias_ocorrencia (id) ON DELETE CASCADE
                );

                DROP TRIGGER IF EXISTS trg_historico_ocorrencias_status;
                CREATE TRIGGER trg_historico_ocorrencias_status
                AFTER UPDATE OF status ON ocorrencias_ocorrencia
                WHEN OLD.status IS NOT NEW.status
                BEGIN
                    INSERT INTO historico_ocorrencias (ocorrencia_id, status_anterior, status_novo, data_alteracao)
                    VALUES (NEW.id, OLD.status, NEW.status, CURRENT_TIMESTAMP);
                END;

                CREATE INDEX IF NOT EXISTS idx_contas_usuario_email ON contas_usuario (email);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_status ON ocorrencias_ocorrencia (status);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_bairro ON ocorrencias_ocorrencia (bairro);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_numero_poste ON ocorrencias_ocorrencia (numero_poste);
                CREATE INDEX IF NOT EXISTS idx_ocorrencias_data_registro ON ocorrencias_ocorrencia (data_registro);

                DROP VIEW IF EXISTS vw_painel_ocorrencias_ativas;
                CREATE VIEW vw_painel_ocorrencias_ativas AS
                SELECT
                    o.id,
                    o.protocolo,
                    o.numero_poste,
                    o.logradouro,
                    o.rua,
                    o.bairro,
                    o.ponto_referencia,
                    o.tipo_defeito,
                    o.status,
                    o.data_registro,
                    o.cidadao_id,
                    COALESCE(NULLIF(u.nome_completo, ''), o.nome_cidadao_snapshot, u.username) AS nome_completo,
                    COALESCE(NULLIF(u.cpf, ''), o.cpf_cidadao_snapshot) AS cpf
                FROM ocorrencias_ocorrencia o
                LEFT JOIN contas_usuario u ON o.cidadao_id = u.id
                WHERE o.status IN ('Pendente', 'Em progresso');
            """)


def revert_custom_db_objects(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                DROP VIEW IF EXISTS vw_painel_ocorrencias_ativas;
                DROP VIEW IF EXISTS funcionarios;
                DROP VIEW IF EXISTS cidadao;
                DROP VIEW IF EXISTS ocorrencias;

                DROP INDEX IF EXISTS idx_ocorrencias_data_registro;
                DROP INDEX IF EXISTS idx_ocorrencias_numero_poste;
                DROP INDEX IF EXISTS idx_ocorrencias_bairro;
                DROP INDEX IF EXISTS idx_ocorrencias_status;

                DROP INDEX IF EXISTS idx_funcionario_email;
                DROP INDEX IF EXISTS idx_cidadao_email;
                DROP INDEX IF EXISTS idx_contas_usuario_email;

                DROP TRIGGER IF EXISTS trg_historico_ocorrencias_status ON ocorrencias_ocorrencia;
                DROP FUNCTION IF EXISTS fn_trg_historico_ocorrencias;
                DROP TABLE IF EXISTS historico_ocorrencias;
            """)
        else:
            cursor.execute("""
                DROP VIEW IF EXISTS vw_painel_ocorrencias_ativas;
                DROP TRIGGER IF EXISTS trg_historico_ocorrencias_status;
                DROP TABLE IF EXISTS historico_ocorrencias;
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0002_ocorrencia_atendente'),
        ('contas', '0003_historicoauditoria_ocorrencia_and_more'),
    ]

    operations = [
        migrations.RunPython(apply_custom_db_objects, revert_custom_db_objects),
    ]
