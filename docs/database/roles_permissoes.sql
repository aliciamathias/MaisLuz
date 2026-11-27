-- ==============================================================================
-- SISTEMA MAISLUZ - DDL: ROLES E PERMISSÕES (RBAC)
-- Banco de Dados: PostgreSQL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. CRIAÇÃO DAS ROLES COM LOGIN E SENHA
-- ------------------------------------------------------------------------------
DO $$
BEGIN
    -- Role de Suporte
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'suporte_maisluz') THEN
        CREATE ROLE suporte_maisluz WITH LOGIN PASSWORD 'SenhaSuporte123456';
    ELSE
        ALTER ROLE suporte_maisluz WITH LOGIN PASSWORD 'SenhaSuporte123456';
    END IF;

    -- Role de Desenvolvimento
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dev_maisluz') THEN
        CREATE ROLE dev_maisluz WITH LOGIN PASSWORD 'SenhaDev123456';
    ELSE
        ALTER ROLE dev_maisluz WITH LOGIN PASSWORD 'SenhaDev123456';
    END IF;
END
$$;

-- ------------------------------------------------------------------------------
-- 2. CONCESSÃO DE ACESSO AO BANCO E AO SCHEMA PUBLIC
-- ------------------------------------------------------------------------------
GRANT CONNECT ON DATABASE maisluz TO suporte_maisluz, dev_maisluz;
GRANT USAGE ON SCHEMA public TO suporte_maisluz, dev_maisluz;

-- ------------------------------------------------------------------------------
-- 3. PERMISSÕES DE TABELAS (SELECT, INSERT, UPDATE)
-- ------------------------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO suporte_maisluz, dev_maisluz;

-- Permissão necessária em sequences para permitir INSERTs com auto-incremento (SERIAL/BIGSERIAL)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO suporte_maisluz, dev_maisluz;

-- Garante que futuras tabelas e sequências criadas no schema public herdem essas permissões
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO suporte_maisluz, dev_maisluz;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO suporte_maisluz, dev_maisluz;

-- ------------------------------------------------------------------------------
-- 4. REVOGAÇÃO EXPLÍCITA DE DELETE EM TODAS AS TABELAS
-- ------------------------------------------------------------------------------
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM suporte_maisluz, dev_maisluz;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE DELETE ON TABLES FROM suporte_maisluz, dev_maisluz;
