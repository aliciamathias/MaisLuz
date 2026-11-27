-- ==============================================================================
-- SISTEMA MAISLUZ - DDL: CONSTRAINTS CHECK
-- Banco de Dados: PostgreSQL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. CONSTRAINT CHECK: NOME COMPLETO DE FUNCIONÁRIO E CIDADÃO >= 3 CARACTERES
-- Tabela: contas_usuario
-- Regra: Todo nome completo informado para cidadão ou funcionário (desconsiderando
-- espaços nas pontas) deve ter no mínimo 3 caracteres. Permite superusuários ou
-- registros vazios iniciais de sistema antes do preenchimento de perfil.
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- 2. CONSTRAINT CHECK: STATUS DE OCORRÊNCIAS VÁLIDO
-- Tabela: ocorrencias_ocorrencia
-- Regra: Apenas aceita os status permitidos:
--   - 'Pendente' / 'pendente'
--   - 'Em progresso' / 'em progresso'
--   - 'Concluído' / 'concluído' (e variações sem acento)
--   - 'Excluído' / 'excluído' (incluindo exclusão lógica pelo cidadão e funcionário)
-- ------------------------------------------------------------------------------
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

-- View sinônimo de compatibilidade para consultas com "ocorrencias_ocorrencias"
CREATE OR REPLACE VIEW ocorrencias_ocorrencias AS
SELECT * FROM ocorrencias_ocorrencia;
