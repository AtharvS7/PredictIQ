-- ============================================================
-- Predictify — Migration 002: Add RBAC Role Column
-- Adds role-based access control to the profiles table.
-- Roles: admin, editor (default), viewer
-- ============================================================

-- Add role column with CHECK constraint
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'editor'
  CHECK (role IN ('admin', 'editor', 'viewer'));

-- Index for role-based queries (e.g., list all admins)
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

-- Add email column to profiles for admin user listing
-- (synced from Firebase on login)
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS email TEXT;

CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
