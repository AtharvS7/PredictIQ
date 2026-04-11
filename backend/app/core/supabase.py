"""
PredictIQ Supabase Client
Singleton client for Supabase interactions.
"""
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create a Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    return _supabase_client


def get_supabase_admin() -> Client:
    """Get Supabase client with service role key for admin operations."""
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
    return get_supabase()
