"""Simple unit tests that don't require external services."""

import pytest
from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class TestUserModel:
    """Test User model without database."""

    def test_user_model_creation(self):
        """Test creating a user model instance."""
        user_data = {
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
        }

        # Create user instance (without saving to DB)
        user = User(**user_data)

        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.id is None  # Not saved yet

    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            password_hash="hash",
            full_name="Test User"
        )
        expected = "<User(email=test@example.com, full_name=Test User)>"
        assert repr(user) == expected


class TestUserSchemas:
    """Test user Pydantic schemas."""

    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        user_data = {
            "email": "test@example.com",
            "password": "strongpassword",
            "full_name": "Test User"
        }

        user_create = UserCreate(**user_data)

        assert user_create.email == "test@example.com"
        assert user_create.password == "strongpassword"
        assert user_create.full_name == "Test User"

    def test_user_update_schema(self):
        """Test UserUpdate schema validation."""
        update_data = {
            "full_name": "Updated Name",
            "is_active": False
        }

        user_update = UserUpdate(**update_data)

        assert user_update.full_name == "Updated Name"
        assert user_update.is_active is False
        assert user_update.email is None  # Not provided
        assert user_update.password is None  # Not provided


class TestUserValidation:
    """Test user validation logic."""

    def test_email_validation(self):
        """Test email format validation."""
        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.com"
        ]

        for email in valid_emails:
            user_data = {"email": email, "password": "password123"}
            user_create = UserCreate(**user_data)
            assert user_create.email == email

        # Invalid emails should raise validation error
        import pytest
        from pydantic import ValidationError

        invalid_emails = [
            "not-an-email",
            "user@",
            "@domain.com",
            "user..name@domain.com"
        ]

        for email in invalid_emails:
            user_data = {"email": email, "password": "password123"}
            with pytest.raises(ValidationError):
                UserCreate(**user_data)

    def test_password_validation(self):
        """Test password requirements."""
        # Valid passwords
        valid_passwords = [
            "password123",
            "P@ssw0rd!",
            "my-secret-key"
        ]

        for password in valid_passwords:
            user_data = {"email": "test@example.com", "password": password}
            user_create = UserCreate(**user_data)
            assert user_create.password == password

    def test_user_status_defaults(self):
        """Test default user status values."""
        user_data = {
            "email": "test@example.com",
            "password": "password123"
        }

        user_create = UserCreate(**user_data)

        # Check that defaults are applied correctly in the model
        assert user_create.email == "test@example.com"
        assert user_create.password == "password123"
        # is_active and is_superuser are handled at the database level


def test_count_by_user_method():
    """Test that CRUDUser has the count_by_user method."""
    # Check if the method exists
    assert hasattr(CRUDUser, 'count_by_user')
    assert callable(getattr(CRUDUser, 'count_by_user'))