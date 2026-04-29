-- ============================================================
-- Predictify — Neon PostgreSQL Initial Schema
-- Migrated from Supabase
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Profiles ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id          TEXT PRIMARY KEY,
    full_name   TEXT,
    avatar_url  TEXT,
    hourly_rate_usd DOUBLE PRECISION DEFAULT 75.0,
    currency    TEXT DEFAULT 'USD',
    theme       TEXT DEFAULT 'system',
    timezone    TEXT DEFAULT 'UTC',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── Document Uploads ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS document_uploads (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             TEXT NOT NULL,
    storage_path        TEXT,
    original_filename   TEXT NOT NULL,
    file_size_bytes     BIGINT DEFAULT 0,
    mime_type           TEXT,
    status              TEXT DEFAULT 'uploaded',
    parsed_text_preview TEXT,
    file_data           BYTEA,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_uploads_user_id ON document_uploads(user_id);

-- ── Estimates ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS estimates (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 TEXT NOT NULL,
    document_id             UUID REFERENCES document_uploads(id),
    project_name            TEXT NOT NULL,
    version                 INTEGER DEFAULT 1,
    status                  TEXT DEFAULT 'complete',
    inputs_json             JSONB,
    outputs_json            JSONB,
    effort_likely_hours     DOUBLE PRECISION,
    cost_likely_usd         DOUBLE PRECISION,
    duration_likely_weeks   DOUBLE PRECISION,
    risk_score              DOUBLE PRECISION,
    confidence_pct          DOUBLE PRECISION,
    model_version           TEXT DEFAULT '1.0.0',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_estimates_user_id ON estimates(user_id);
CREATE INDEX IF NOT EXISTS idx_estimates_status ON estimates(status);
CREATE INDEX IF NOT EXISTS idx_estimates_created_at ON estimates(created_at DESC);

-- ── Share Links ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS share_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estimate_id     UUID NOT NULL REFERENCES estimates(id),
    token           TEXT NOT NULL UNIQUE,
    password_hash   TEXT,
    expires_at      TIMESTAMPTZ,
    view_count      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_share_links_token ON share_links(token);
