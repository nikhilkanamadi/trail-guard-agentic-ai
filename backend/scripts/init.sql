-- TrialGuard AI — PostgreSQL Initialization Script
-- This script runs on first database creation via Docker entrypoint

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create enum types
DO $$ BEGIN
    CREATE TYPE study_phase AS ENUM ('I', 'II', 'III', 'IV', 'I/II', 'II/III');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE study_status AS ENUM ('draft', 'active', 'enrolling', 'closed', 'archived');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE document_status AS ENUM ('pending', 'processing', 'validated', 'failed', 'needs_review');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE finding_severity AS ENUM ('critical', 'major', 'minor', 'info');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE finding_status AS ENUM ('open', 'acknowledged', 'resolved', 'false_positive', 'escalated');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'validator', 'reviewer', 'auditor', 'read_only');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE validation_run_type AS ENUM ('full', 'incremental', 're_validation');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE validation_run_status AS ENUM ('queued', 'running', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Audit trail protection: prevent updates and deletes
-- This will be applied after the ORM creates the table via Alembic
-- CREATE OR REPLACE FUNCTION prevent_audit_modification()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     RAISE EXCEPTION 'Audit trail records cannot be modified or deleted (21 CFR Part 11)';
--     RETURN NULL;
-- END;
-- $$ LANGUAGE plpgsql;

-- Grant appropriate permissions
GRANT ALL PRIVILEGES ON DATABASE trialguard_db TO trialguard;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'TrialGuard AI database initialized successfully';
END $$;
