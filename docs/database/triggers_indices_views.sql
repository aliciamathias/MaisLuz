-- ==============================================================================
-- SISTEMA MAISLUZ - DDL: TABELAS, TRIGGERS, ÍNDICES E VIEWS
-- Banco de Dados: PostgreSQL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. TABELA DE HISTÓRICO DE OCORRÊNCIAS
-- ------------------------------------------------------------------------------
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

-- ------------------------------------------------------------------------------
-- 2. FUNÇÃO E TRIGGER PARA HISTÓRICO DE MUDANÇA DE STATUS
-- Dispara toda vez que a coluna 'status' da ocorrência for alterada.
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- 3. CRIAÇÃO DE ÍNDICES E ANÁLISE DE CHAVES PRIMÁRIAS / UNIQUE EXISTENTES
-- Regra: Evitar criar índices onde já existe PRIMARY KEY ou UNIQUE constraint
-- ------------------------------------------------------------------------------

-- Tabela: contas_usuario (Cidadãos e Funcionários)
-- [JÁ EXISTE UNIQUE]:
--   - cpf: possui restrição UNIQUE ('contas_usuario_cpf_key'), índice dispensado.
--   - matricula_funcional: possui restrição UNIQUE ('contas_usuario_matricula_funcional_key'), índice dispensado.
-- [NÃO POSSUI UNIQUE]:
--   - email: campo não-único, necessita de índice para otimização de busca e login.
CREATE INDEX IF NOT EXISTS idx_contas_usuario_email ON contas_usuario (email);
CREATE INDEX IF NOT EXISTS idx_cidadao_email ON contas_usuario (email) WHERE tipo_perfil = 'CIDADAO';
CREATE INDEX IF NOT EXISTS idx_funcionario_email ON contas_usuario (email) WHERE tipo_perfil = 'FUNCIONARIO';

-- Tabela: ocorrencias_ocorrencia
-- [JÁ EXISTE UNIQUE / PK]:
--   - id: PRIMARY KEY ('ocorrencias_ocorrencia_pkey'), índice dispensado.
--   - protocolo: possui restrição UNIQUE ('ocorrencias_ocorrencia_protocolo_key'), índice dispensado.
-- [ÍNDICES DE BUSCA E FILTROS]:
CREATE INDEX IF NOT EXISTS idx_ocorrencias_status ON ocorrencias_ocorrencia (status);
CREATE INDEX IF NOT EXISTS idx_ocorrencias_bairro ON ocorrencias_ocorrencia (bairro);
CREATE INDEX IF NOT EXISTS idx_ocorrencias_numero_poste ON ocorrencias_ocorrencia (numero_poste);
CREATE INDEX IF NOT EXISTS idx_ocorrencias_data_registro ON ocorrencias_ocorrencia (data_registro);


-- ------------------------------------------------------------------------------
-- 4. VIEWS DE SUPORTE E ALIASES
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW ocorrencias AS
SELECT * FROM ocorrencias_ocorrencia;

CREATE OR REPLACE VIEW cidadao AS
SELECT * FROM contas_usuario WHERE tipo_perfil = 'CIDADAO';

CREATE OR REPLACE VIEW funcionarios AS
SELECT * FROM contas_usuario WHERE tipo_perfil = 'FUNCIONARIO';


-- ------------------------------------------------------------------------------
-- 5. VIEW DO PAINEL DE OCORRÊNCIAS ATIVAS (vw_painel_ocorrencias_ativas)
-- Retorna os dados da ocorrência e do cidadão solicitante, filtrando apenas
-- ocorrências ativas ('Pendente' e 'Em progresso'), ignorando concluídas ou excluídas.
-- ------------------------------------------------------------------------------
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
