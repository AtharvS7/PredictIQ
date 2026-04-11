-- ═══════════════════════════════════════════════════════════════
-- PredictIQ — Initial Database Schema
-- Migration 001: Create all application tables
-- ═══════════════════════════════════════════════════════════════

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────────────────────
-- TABLE: profiles
-- Stores user profile data; linked 1:1 to auth.users via id.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    hourly_rate_usd NUMERIC(10, 2) DEFAULT 75.00,
    currency TEXT DEFAULT 'USD',
    theme TEXT DEFAULT 'system',
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_profiles_id ON public.profiles(id);

COMMENT ON TABLE public.profiles IS 'User profile data linked to Supabase Auth users.';

-- ──────────────────────────────────────────────────────────────
-- TABLE: document_uploads
-- Tracks uploaded project specification documents.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.document_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    storage_path TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type TEXT,
    status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'parsed', 'failed')),
    parsed_text_preview TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_document_uploads_user_id ON public.document_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_document_uploads_created_at ON public.document_uploads(created_at DESC);

COMMENT ON TABLE public.document_uploads IS 'Metadata for uploaded project specification documents.';

-- ──────────────────────────────────────────────────────────────
-- TABLE: estimates
-- Core table storing all generated cost/effort estimates.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.estimates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    document_id UUID REFERENCES public.document_uploads(id) ON DELETE SET NULL,
    project_name TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT 'complete' CHECK (status IN ('processing', 'complete', 'failed', 'deleted')),
    inputs_json JSONB NOT NULL DEFAULT '{}',
    outputs_json JSONB NOT NULL DEFAULT '{}',
    effort_likely_hours NUMERIC(12, 2),
    cost_likely_usd NUMERIC(14, 2),
    duration_likely_weeks NUMERIC(8, 2),
    risk_score NUMERIC(5, 2),
    confidence_pct NUMERIC(5, 2),
    model_version TEXT DEFAULT '2.0.0',
    share_token TEXT UNIQUE,
    share_password_hash TEXT,
    share_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_estimates_user_id ON public.estimates(user_id);
CREATE INDEX IF NOT EXISTS idx_estimates_created_at ON public.estimates(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_estimates_status ON public.estimates(status);
CREATE INDEX IF NOT EXISTS idx_estimates_share_token ON public.estimates(share_token) WHERE share_token IS NOT NULL;

COMMENT ON TABLE public.estimates IS 'Generated cost/effort/timeline estimates from ML model.';

-- ──────────────────────────────────────────────────────────────
-- AUTO-CREATE PROFILE ON SIGNUP
-- Trigger: inserts a profiles row when a new auth.users row appears.
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data ->> 'full_name',
        NEW.raw_user_meta_data ->> 'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
