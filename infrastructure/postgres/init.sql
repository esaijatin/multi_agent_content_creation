-- AstraOS PostgreSQL initialization (Phase 1)
-- Extensions and base schema; Alembic migrations extend this in later phases.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Roles for RBAC (Phase 5 expands)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'astraos_app') THEN
    CREATE ROLE astraos_app;
  END IF;
END
$$;

-- Audit log helper
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
