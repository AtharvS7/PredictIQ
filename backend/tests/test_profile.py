"""
Predictify — Profile Module Tests
Tests for ALLOWED_PROFILE_COLUMNS allowlist and _build_update_query() SQL safety.
"""
import pytest
from fastapi import HTTPException
from app.api.v1.profile import (
    ALLOWED_PROFILE_COLUMNS, _build_update_query, ProfileUpdate,
)


class TestAllowedColumns:
    """Verify the column allowlist is correct."""

    def test_allowlist_is_frozenset(self):
        """Allowlist should be an immutable frozenset."""
        assert isinstance(ALLOWED_PROFILE_COLUMNS, frozenset)

    def test_expected_columns_present(self):
        """All expected profile columns should be in the allowlist."""
        expected = {"full_name", "avatar_url", "hourly_rate_usd",
                    "currency", "theme", "timezone"}
        assert expected == ALLOWED_PROFILE_COLUMNS

    def test_no_dangerous_columns(self):
        """Dangerous columns should NOT be in the allowlist."""
        dangerous = {"id", "user_id", "created_at", "updated_at",
                     "password", "role", "admin", "is_admin", "email"}
        for col in dangerous:
            assert col not in ALLOWED_PROFILE_COLUMNS, f"Dangerous column '{col}' in allowlist"

    def test_allowlist_not_empty(self):
        """Allowlist should have at least one column."""
        assert len(ALLOWED_PROFILE_COLUMNS) >= 1


class TestBuildUpdateQuery:
    """Tests for _build_update_query() SQL builder."""

    def test_single_field_update(self):
        """Single field should produce valid query."""
        query, values = _build_update_query({"full_name": "John"})
        assert "full_name = $2" in query
        assert "UPDATE profiles SET" in query
        assert "WHERE id = $1" in query
        assert values == ["John"]

    def test_multiple_fields_update(self):
        """Multiple fields should produce parameterized query."""
        query, values = _build_update_query({
            "full_name": "Jane",
            "currency": "EUR",
        })
        assert "$2" in query
        assert "$3" in query
        assert "WHERE id = $1" in query
        assert len(values) == 2

    def test_filters_disallowed_columns(self):
        """Columns not in allowlist should be silently dropped."""
        query, values = _build_update_query({
            "full_name": "John",
            "admin": True,  # NOT in allowlist
            "role": "superuser",  # NOT in allowlist
        })
        assert "admin" not in query
        assert "role" not in query
        assert "full_name" in query
        assert values == ["John"]

    def test_empty_updates_raises(self):
        """Empty update dict should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            _build_update_query({})
        assert exc_info.value.status_code == 400

    def test_all_disallowed_raises(self):
        """Dict with only disallowed columns should raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            _build_update_query({"password": "hacked", "role": "admin"})
        assert exc_info.value.status_code == 400

    def test_query_has_returning(self):
        """Query should include RETURNING clause."""
        query, _ = _build_update_query({"theme": "dark"})
        assert "RETURNING" in query

    def test_query_updates_timestamp(self):
        """Query should set updated_at = NOW()."""
        query, _ = _build_update_query({"timezone": "UTC"})
        assert "updated_at = NOW()" in query

    def test_sql_injection_in_value_parameterized(self):
        """SQL injection in values should be safely parameterized."""
        query, values = _build_update_query({
            "full_name": "'; DROP TABLE profiles; --"
        })
        # The malicious string should be in values (parameterized),
        # NOT interpolated into the query string
        assert "DROP TABLE" not in query
        assert "'; DROP TABLE profiles; --" in values

    def test_sql_injection_in_key_blocked(self):
        """SQL injection via column names should be blocked by allowlist."""
        query, values = _build_update_query({
            "full_name": "safe",
            "1=1; DROP TABLE profiles; --": "attack",
        })
        assert "DROP TABLE" not in query
        assert len(values) == 1  # Only the safe field


class TestProfileUpdateModel:
    """Tests for ProfileUpdate Pydantic model."""

    def test_all_fields_optional(self):
        """ProfileUpdate should be creatable with no fields."""
        update = ProfileUpdate()
        assert update.full_name is None
        assert update.currency is None

    def test_partial_update(self):
        """Partial field updates should work."""
        update = ProfileUpdate(full_name="Test", theme="dark")
        assert update.full_name == "Test"
        assert update.theme == "dark"
        assert update.currency is None

    def test_hourly_rate_is_float(self):
        """hourly_rate_usd should accept floats."""
        update = ProfileUpdate(hourly_rate_usd=125.50)
        assert update.hourly_rate_usd == 125.50
