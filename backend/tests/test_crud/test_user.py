"""Tests for user CRUD operations."""

import pytest

from app.crud.user import user as user_crud
from app.schemas.auth import UserCreate, UserUpdate


@pytest.mark.unit
class TestUserCRUD:
    """Test user CRUD operations."""

    async def test_create_user(self, test_db_session):
        """Test creating a new user."""
        user_data = UserCreate(
            email="test@example.com",
            password="TestPassword123!"
        )

        user = await user_crud.create(test_db_session, obj_in=user_data)

        assert user is not None
        assert user.email == user_data.email
        assert user.hashed_password is not None
        assert user.hashed_password != user_data.password  # Should be hashed
        assert user.id is not None
        assert user.is_active is True

    async def test_get_user_by_id(self, test_db_session, test_user):
        """Test getting a user by ID."""
        user = await user_crud.get(test_db_session, id=test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_by_email(self, test_db_session, test_user):
        """Test getting a user by email."""
        user = await user_crud.get_by_email(test_db_session, email=test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_by_id_not_found(self, test_db_session):
        """Test getting a non-existent user by ID."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        user = await user_crud.get(test_db_session, id=fake_id)

        assert user is None

    async def test_get_user_by_email_not_found(self, test_db_session):
        """Test getting a non-existent user by email."""
        user = await user_crud.get_by_email(test_db_session, email="nonexistent@example.com")

        assert user is None

    async def test_update_user_email(self, test_db_session, test_user):
        """Test updating a user's email."""
        update_data = UserUpdate(email="updated@example.com")
        updated_user = await user_crud.update(
            test_db_session,
            db_obj=test_user,
            obj_in=update_data
        )

        assert updated_user.email == "updated@example.com"
        assert updated_user.id == test_user.id

    async def test_update_user_password(self, test_db_session, test_user):
        """Test updating a user's password."""
        new_password = "NewPassword123!"
        update_data = UserUpdate(password=new_password)
        updated_user = await user_crud.update(
            test_db_session,
            db_obj=test_user,
            obj_in=update_data
        )

        # Password should be hashed and different from original
        assert updated_user.hashed_password != test_user.hashed_password
        # Verify the new password can be verified
        from app.core.security import verify_password
        assert verify_password(new_password, updated_user.hashed_password)

    async def test_authenticate_user_valid_credentials(self, test_db_session, test_user, test_password):
        """Test authenticating a user with valid credentials."""
        authenticated_user = await user_crud.authenticate(
            test_db_session,
            email=test_user.email,
            password=test_password
        )

        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id

    async def test_authenticate_user_invalid_email(self, test_db_session):
        """Test authenticating with invalid email."""
        authenticated_user = await user_crud.authenticate(
            test_db_session,
            email="invalid@example.com",
            password="any-password"
        )

        assert authenticated_user is None

    async def test_authenticate_user_invalid_password(self, test_db_session, test_user):
        """Test authenticating with invalid password."""
        authenticated_user = await user_crud.authenticate(
            test_db_session,
            email=test_user.email,
            password="wrong-password"
        )

        assert authenticated_user is None

    async def test_is_active_user_active(self, test_db_session, test_user):
        """Test checking if an active user is active."""
        assert await user_crud.is_active(test_user) is True

    async def test_delete_user(self, test_db_session, test_user):
        """Test deleting a user."""
        deleted_user = await user_crud.delete(test_db_session, id=test_user.id)

        assert deleted_user.id == test_user.id

        # Verify user is deleted
        user = await user_crud.get(test_db_session, id=test_user.id)
        assert user is None

    async def test_count_users(self, test_db_session, test_user):
        """Test counting users."""
        count = await user_crud.count_by_user(test_db_session, user_id=test_user.id)
        assert count == 1