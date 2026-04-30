"""
Predictify — Security Module Tests
Tests for CurrentUser model and auth utility structures.
"""
import pytest
from app.core.security import CurrentUser


class TestCurrentUserModel:
    """Tests for the CurrentUser Pydantic model."""

    def test_basic_creation(self):
        """CurrentUser should be creatable with just an id."""
        user = CurrentUser(id="user-123")
        assert user.id == "user-123"

    def test_email_optional(self):
        """Email should be optional and default to None."""
        user = CurrentUser(id="user-123")
        assert user.email is None

    def test_email_set(self):
        """Email should be settable."""
        user = CurrentUser(id="user-123", email="test@example.com")
        assert user.email == "test@example.com"

    def test_default_role(self):
        """Default role should be 'authenticated'."""
        user = CurrentUser(id="user-123")
        assert user.role == "authenticated"

    def test_custom_role(self):
        """Custom role should be accepted."""
        user = CurrentUser(id="user-123", role="admin")
        assert user.role == "admin"

    def test_full_creation(self):
        """All fields should work together."""
        user = CurrentUser(
            id="firebase-uid-abc",
            email="admin@predictify.app",
            role="admin",
        )
        assert user.id == "firebase-uid-abc"
        assert user.email == "admin@predictify.app"
        assert user.role == "admin"

    def test_id_required(self):
        """Creating without id should raise validation error."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            CurrentUser()

    def test_dict_serialization(self):
        """Model should serialize to dict correctly."""
        user = CurrentUser(id="user-123", email="a@b.com")
        d = user.model_dump()
        assert d["id"] == "user-123"
        assert d["email"] == "a@b.com"
        assert d["role"] == "authenticated"

    def test_json_serialization(self):
        """Model should serialize to JSON string."""
        user = CurrentUser(id="user-123")
        json_str = user.model_dump_json()
        assert "user-123" in json_str
        assert "authenticated" in json_str
