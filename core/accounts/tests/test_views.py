import pytest
from django.urls import reverse
from accounts.models import Profile, User
from todo.models import Task


@pytest.fixture
def common_user():
    user = User.objects.create_user(
        email="admin@admin.com", password="a/@1234567", is_verified=True
    )
    return user


@pytest.mark.django_db
class TestRegisterPage:
    """Test suite for RegisterPage view"""

    def test_register_page_get(self, client):
        """Test GET request to register page"""
        url = reverse("accounts:register")
        response = client.get(url)
        assert response.status_code == 200

    def test_register_page_redirects_if_authenticated(self, client, common_user):
        """Test that authenticated users are redirected from register page"""
        user = common_user
        client.force_login(user)
        # api_client.force_authenticate(user=user)
        url = reverse("accounts:register")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == "/"

    def test_register_page_post_valid(self, client):
        """Test POST request with valid registration data"""
        url = reverse("accounts:register")
        data = {
            "email": "newuser@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(email="newuser@example.com").exists()
        # User should be logged in after registration
        user = User.objects.get(email="newuser@example.com")
        assert hasattr(user, "profile")

    def test_register_page_post_invalid(self, client):
        """Test POST request with invalid registration data"""
        url = reverse("accounts:register")
        data = {"email": "invalid-email", "password1": "pass", "password2": "pass"}
        response = client.post(url, data)
        assert response.status_code == 200  # Returns form with errors
        assert not User.objects.filter(email="invalid-email").exists()

    def test_register_page_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        url = reverse("accounts:register")
        data = {
            "email": "newuser@example.com",
            "password1": "ComplexPass123!",
            "password2": "DifferentPass123!",
        }
        response = client.post(url, data)
        assert response.status_code == 200  # Returns form with errors
        assert not User.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
class TestCustomLoginView:
    """Test suite for CustomLoginView"""

    def test_login_page_get(self, client, common_user):
        """Test GET request to login page"""
        url = reverse("accounts:login")
        response = client.get(url)
        assert response.status_code == 200
        assert "login.html" in [t.name for t in response.templates]

    def test_login_page_redirects_if_authenticated(self, client, common_user):
        """Test that authenticated users are redirected from login page"""
        client.force_login(common_user)
        url = reverse("accounts:login")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == "/"

    def test_login_post_valid(self, client, common_user):
        client.logout()
        url = reverse("accounts:login")
        data = {"username": common_user.email, "password": "a/@1234567"}
        response = client.post(url, data)
        assert response.status_code == 302
        assert "_auth_user_id" in client.session

    def test_login_post_invalid(self, client, common_user):
        """Test POST request with invalid login credentials"""
        url = reverse("accounts:login")
        data = {"email": common_user.email, "password": "wrongpassword"}
        response = client.post(url, data)
        assert response.status_code == 200

    def test_login_post_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        url = reverse("accounts:login")
        data = {"email": "nonexistent@example.com", "password": "somepassword"}
        response = client.post(url, data)
        assert response.status_code == 200  # Returns form with errors


@pytest.mark.django_db
class TestCustomLogoutView:
    """Test suite for CustomLogoutView"""

    def test_logout_requires_login(self, client):
        """Test that logout requires authentication"""
        url = reverse("accounts:logout")
        response = client.get(url)
        # Django logout view redirects even if not logged in
        assert response.status_code == 302

    def test_logout_success(self, client, common_user):
        """Test successful logout"""
        client.force_login(common_user)
        url = reverse("accounts:logout")
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == "/"
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200
