"""
PredictIQ Supabase Client
Singleton clients for Supabase interactions.
"""
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Client | None = None
_supabase_admin: Client | None = None


def get_supabase() -> Client:
    """Get or create a Supabase client instance (anon key — for auth only)."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    return _supabase_client


def get_supabase_admin() -> Client:
    """
    Get Supabase client with service role key for database operations.
    The service role bypasses RLS, so the backend can perform DB operations
    on behalf of verified users after auth.get_user() validation.
    """
    global _supabase_admin
    if _supabase_admin is None:
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            _supabase_admin = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        else:
            # Fallback to anon key if no service role key
            _supabase_admin = get_supabase()
    return _supabase_admin
