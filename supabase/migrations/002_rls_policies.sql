-- ═══════════════════════════════════════════════════════════════
-- PredictIQ — Row-Level Security Policies
-- Migration 002: Enable RLS and create access policies
-- ═══════════════════════════════════════════════════════════════

-- ──────────────────────────────────────────────────────────────
-- PROFILES: Users can only read/update their own profile
-- ──────────────────────────────────────────────────────────────
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ──────────────────────────────────────────────────────────────
-- DOCUMENT_UPLOADS: Users can only access their own documents
-- ──────────────────────────────────────────────────────────────
ALTER TABLE public.document_uploads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own documents"
    ON public.document_uploads FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents"
    ON public.document_uploads FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents"
    ON public.document_uploads FOR DELETE
    USING (auth.uid() = user_id);

-- ──────────────────────────────────────────────────────────────
-- ESTIMATES: Users can only access their own non-deleted estimates
-- ──────────────────────────────────────────────────────────────
ALTER TABLE public.estimates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own active estimates"
    ON public.estimates FOR SELECT
    USING (auth.uid() = user_id AND status != 'deleted');

CREATE POLICY "Users can insert own estimates"
    ON public.estimates FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own estimates"
    ON public.estimates FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own estimates"
    ON public.estimates FOR DELETE
    USING (auth.uid() = user_id);

-- ──────────────────────────────────────────────────────────────
-- STORAGE: project-docs bucket policies
-- Users can upload/read/delete files in their own folder.
-- Storage path convention: project-docs/{user_id}/{filename}
-- ──────────────────────────────────────────────────────────────
-- NOTE: Run these in the Supabase Dashboard → Storage → Policies
-- or via the Supabase SQL Editor after creating the bucket.

-- INSERT (upload): authenticated users can upload to their own folder
CREATE POLICY "Users can upload to own folder"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'project-docs'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- SELECT (download): authenticated users can read their own files
CREATE POLICY "Users can read own files"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'project-docs'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- DELETE: authenticated users can delete their own files
CREATE POLICY "Users can delete own files"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'project-docs'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );
