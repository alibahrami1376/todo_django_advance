import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from accounts.models import User, Profile
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    """Create a verified user for testing"""
    user = User.objects.create_user(
        email="testuser@example.com", password="testpass123", is_verified=True
    )
    return user


@pytest.fixture
def unverified_user(db):
    """Create an unverified user for testing"""
    user = User.objects.create_user(
        email="unverified@example.com", password="testpass123", is_verified=False
    )
    return user


@pytest.fixture
def profile(user):
    """Create a profile for the user"""
    return user.profile


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client"""
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return api_client


@pytest.mark.django_db
class TestRegistrationApiView:
    """Test suite for RegistrationApiView"""

    def test_registration_success(self, api_client):
        """Test successful user registration"""
        url = reverse("accounts:api-v1:registration")
        data = {
            "email": "newuser@example.com",
            "password": "ComplexPass123!",
            "password1": "ComplexPass123!",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "email" in response.data
        assert User.objects.filter(email="newuser@example.com").exists()
        # User should not be verified initially
        user = User.objects.get(email="newuser@example.com")
        assert user.is_verified is False
        # Profile should be created
        assert hasattr(user, "profile")

    def test_registration_password_mismatch(self, api_client):
        """Test registration with mismatched passwords"""
        url = reverse("accounts:api-v1:registration")
        data = {
            "email": "newuser@example.com",
            "password": "ComplexPass123!",
            "password1": "DifferentPass123!",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_registration_duplicate_email(self, api_client, user):
        """Test registration with duplicate email"""
        url = reverse("accounts:api-v1:registration")
        data = {
            "email": user.email,
            "password": "ComplexPass123!",
            "password1": "ComplexPass123!",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_weak_password(self, api_client):
        """Test registration with weak password"""
        url = reverse("accounts:api-v1:registration")
        data = {"email": "newuser@example.com", "password": "123", "password1": "123"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Password validation errors are returned in non_field_errors
        assert "non_field_errors" in response.data


@pytest.mark.django_db
class TestCustomAuthToken:
    """Test suite for CustomAuthToken"""

    def test_token_login_success(self, api_client, user):
        """Test successful token authentication"""
        url = reverse("accounts:api-v1:token-login")
        data = {"email": user.email, "password": "testpass123"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert "user_id" in response.data
        assert "email" in response.data
        assert Token.objects.filter(user=user).exists()

    def test_token_login_invalid_credentials(self, api_client, user):
        """Test token login with invalid credentials"""
        url = reverse("accounts:api-v1:token-login")
        data = {"email": user.email, "password": "wrongpassword"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_login_unverified_user(self, api_client, unverified_user):
        """Test that unverified users cannot login"""
        url = reverse("accounts:api-v1:token-login")
        data = {"email": unverified_user.email, "password": "testpass123"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "details" in response.data

    def test_token_login_nonexistent_user(self, api_client):
        """Test token login with nonexistent user"""
        url = reverse("accounts:api-v1:token-login")
        data = {"email": "nonexistent@example.com", "password": "somepassword"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCustomDiscardAuthToken:
    """Test suite for CustomDiscardAuthToken"""

    def test_token_logout_success(self, authenticated_client, user):
        """Test successful token logout"""
        url = reverse("accounts:api-v1:token-logout")
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Token.objects.filter(user=user).exists()

    def test_token_logout_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot logout"""
        url = reverse("accounts:api-v1:token-logout")
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileApiView:
    """Test suite for ProfileApiView"""

    def test_get_profile_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot view profile"""
        url = reverse("accounts:api-v1:profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_authenticated(self, authenticated_client, user, profile):
        """Test that authenticated users can view their profile"""
        url = reverse("accounts:api-v1:profile")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert "first_name" in response.data
        assert "last_name" in response.data

    def test_update_profile_authenticated(self, authenticated_client, profile):
        """Test that authenticated users can update their profile"""
        url = reverse("accounts:api-v1:profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "description": "Updated description",
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        profile.refresh_from_db()
        assert profile.first_name == "Updated"

    def test_partial_update_profile(self, authenticated_client, profile):
        """Test partial update of profile"""
        url = reverse("accounts:api-v1:profile")
        data = {"first_name": "Partially Updated"}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Partially Updated"
        profile.refresh_from_db()
        assert profile.first_name == "Partially Updated"

    def test_profile_email_read_only(self, authenticated_client, user):
        """Test that email field is read-only"""
        url = reverse("accounts:api-v1:profile")
        data = {"first_name": "Test", "email": "hacked@example.com"}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        # Email should remain unchanged
        user.refresh_from_db()
        assert user.email != "hacked@example.com"


@pytest.mark.django_db
class TestChangePasswordApiView:
    """Test suite for ChangePasswordApiView"""

    def test_change_password_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot change password"""
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "oldpass",
            "new_password": "NewPass123!",
            "new_password1": "NewPass123!",
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change"""
        url = reverse("accounts:api-v1:change-password")
        old_password = "testpass123"
        new_password = "NewComplexPass123!"
        data = {
            "old_password": old_password,
            "new_password": new_password,
            "new_password1": new_password,
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "details" in response.data
        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password(new_password)
        assert not user.check_password(old_password)

    def test_change_password_wrong_old_password(self, authenticated_client, user):
        """Test password change with wrong old password"""
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "wrongpassword",
            "new_password": "NewPass123!",
            "new_password1": "NewPass123!",
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_mismatch(self, authenticated_client, user):
        """Test password change with mismatched new passwords"""
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "testpass123",
            "new_password": "NewPass123!",
            "new_password1": "DifferentPass123!",
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_change_password_weak_password(self, authenticated_client, user):
        """Test password change with weak password"""
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "testpass123",
            "new_password": "123",
            "new_password1": "123",
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestActivationApiView:
    """Test suite for ActivationApiView"""

    def test_activation_invalid_token(self, api_client):
        """Test activation with invalid token"""
        url = reverse("accounts:api-v1:activation", kwargs={"token": "invalid_token"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "details" in response.data

    def test_activation_already_verified(self, api_client, user):
        """Test activation of already verified user"""
        from core.settings import SECRET_KEY
        import jwt

        # Create a token with user_id as expected by the view
        token = jwt.encode({"user_id": user.pk}, SECRET_KEY, algorithm="HS256")

        url = reverse("accounts:api-v1:activation", kwargs={"token": token})
        response = api_client.get(url)
        # Should return message that account is already verified
        assert response.status_code == status.HTTP_200_OK
        assert "already" in response.data.get("details", "").lower()

    def test_activation_success(self, api_client, unverified_user):
        """Test successful account activation"""
        from core.settings import SECRET_KEY
        import jwt

        # Create a token with user_id as expected by the view
        token = jwt.encode(
            {"user_id": unverified_user.pk}, SECRET_KEY, algorithm="HS256"
        )

        url = reverse("accounts:api-v1:activation", kwargs={"token": token})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        unverified_user.refresh_from_db()
        assert unverified_user.is_verified is True


@pytest.mark.django_db
class TestActivationResendApiView:
    """Test suite for ActivationResendApiView"""

    def test_resend_activation_nonexistent_user(self, api_client):
        """Test resend activation for nonexistent user"""
        url = reverse("accounts:api-v1:activation-resend")
        data = {"email": "nonexistent@example.com"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_resend_activation_already_verified(self, api_client, user):
        """Test resend activation for already verified user"""
        url = reverse("accounts:api-v1:activation-resend")
        data = {"email": user.email}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data

    def test_resend_activation_success(self, api_client, unverified_user):
        """Test successful resend activation"""
        url = reverse("accounts:api-v1:activation-resend")
        data = {"email": unverified_user.email}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "details" in response.data


@pytest.mark.django_db
class TestJWTAuthentication:
    """Test suite for JWT authentication endpoints"""

    def test_jwt_create_token(self, api_client, user):
        """Test JWT token creation"""
        url = reverse("accounts:api-v1:token_obtain_pair")
        data = {"email": user.email, "password": "testpass123"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_jwt_refresh_token(self, api_client, user):
        """Test JWT token refresh"""
        # First get tokens
        url = reverse("accounts:api-v1:token_obtain_pair")
        data = {"email": user.email, "password": "testpass123"}
        response = api_client.post(url, data)
        refresh_token = response.data["refresh"]

        # Then refresh
        url = reverse("accounts:api-v1:token_refresh")
        data = {"refresh": refresh_token}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_jwt_verify_token(self, api_client, user):
        """Test JWT token verification"""
        # First get tokens
        url = reverse("accounts:api-v1:token_obtain_pair")
        data = {"email": user.email, "password": "testpass123"}
        response = api_client.post(url, data)
        access_token = response.data["access"]

        # Then verify
        url = reverse("accounts:api-v1:token_verify")
        data = {"token": access_token}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
