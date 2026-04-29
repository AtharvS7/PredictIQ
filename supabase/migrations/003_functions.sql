-- ═══════════════════════════════════════════════════════════════
-- Predictify — Database Functions and Triggers
-- Migration 003: Utility functions for the application
-- ═══════════════════════════════════════════════════════════════

-- ──────────────────────────────────────────────────────────────
-- FUNCTION: Auto-update updated_at timestamp
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to estimates table
DROP TRIGGER IF EXISTS set_estimates_updated_at ON public.estimates;
CREATE TRIGGER set_estimates_updated_at
    BEFORE UPDATE ON public.estimates
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Apply to profiles table
DROP TRIGGER IF EXISTS set_profiles_updated_at ON public.profiles;
CREATE TRIGGER set_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- ──────────────────────────────────────────────────────────────
-- FUNCTION: Get user statistics for Dashboard
-- Returns aggregate stats for a given user's estimates.
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.get_user_stats(p_user_id UUID)
RETURNS TABLE (
    total_estimates BIGINT,
    avg_risk_score NUMERIC,
    avg_confidence NUMERIC,
    total_cost_usd NUMERIC,
    avg_cost_usd NUMERIC,
    most_recent_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_estimates,
        ROUND(COALESCE(AVG(e.risk_score), 0), 1) AS avg_risk_score,
        ROUND(COALESCE(AVG(e.confidence_pct), 0), 1) AS avg_confidence,
        ROUND(COALESCE(SUM(e.cost_likely_usd), 0), 2) AS total_cost_usd,
        ROUND(COALESCE(AVG(e.cost_likely_usd), 0), 2) AS avg_cost_usd,
        MAX(e.created_at) AS most_recent_at
    FROM public.estimates e
    WHERE e.user_id = p_user_id
      AND e.status != 'deleted';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ──────────────────────────────────────────────────────────────
-- FUNCTION: Cleanup soft-deleted estimates older than 90 days
-- Can be called by pg_cron or manually for maintenance.
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.cleanup_deleted_estimates()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.estimates
    WHERE status = 'deleted'
      AND updated_at < now() - INTERVAL '90 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
