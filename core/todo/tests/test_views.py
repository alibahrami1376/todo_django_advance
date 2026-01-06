import pytest
from django.urls import reverse
from accounts.models import User, Profile
from todo.models import Task


@pytest.fixture
def user(db):
    """Create a verified user for testing"""
    user = User.objects.create_user(
        email="testuser@example.com", password="testpass123", is_verified=True
    )
    return user


@pytest.fixture
def another_user(db):
    """Create another verified user for testing"""
    user = User.objects.create_user(
        email="anotheruser@example.com", password="testpass123", is_verified=True
    )
    return user


@pytest.fixture
def profile(user):
    """Create a profile for the user"""
    return user.profile


@pytest.fixture
def another_profile(another_user):
    """Create a profile for another user"""
    return another_user.profile


@pytest.fixture
def task(profile):
    """Create a task for testing"""
    return Task.objects.create(
        user=profile,
        title="Test Task",
        description="This is a test task description",
        complete=False,
    )


@pytest.fixture
def completed_task(profile):
    """Create a completed task for testing"""
    return Task.objects.create(
        user=profile,
        title="Completed Task",
        description="This is a completed task",
        complete=True,
    )


@pytest.mark.django_db
class TestTaskListView:
    """Test suite for TaskListView"""

    def test_task_list_unauthenticated(self, client):
        """Test that unauthenticated users are redirected to login"""
        url = reverse("todo:task_list")
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_task_list_authenticated(self, client, user, task, completed_task):
        """Test that authenticated users can view their task list"""
        client.force_login(user)
        url = reverse("todo:task_list")
        response = client.get(url)
        assert response.status_code == 200
        assert "tasks" in response.context
        assert len(response.context["tasks"]) == 2

    def test_task_list_only_own_tasks(self, client, user, another_profile, task):
        """Test that users can only see their own tasks"""
        # Create a task for another user
        another_task = Task.objects.create(
            user=another_profile,
            title="Another User Task",
            description="This is another user's task",
        )

        client.force_login(user)
        url = reverse("todo:task_list")
        response = client.get(url)
        assert response.status_code == 200
        tasks = response.context["tasks"]
        assert len(tasks) == 1
        assert task in tasks
        assert another_task not in tasks


@pytest.mark.django_db
class TestTaskCreateView:
    """Test suite for TaskCreateView"""

    def test_task_create_unauthenticated(self, client):
        """Test that unauthenticated users are redirected to login"""
        url = reverse("todo:create_task")
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_task_create_get_authenticated(self, client, user):
        """Test GET request to create task page"""
        client.force_login(user)
        url = reverse("todo:create_task")
        response = client.get(url)
        assert response.status_code == 200

    def test_task_create_post_authenticated(self, client, user, profile):
        """Test POST request to create a task"""
        client.force_login(user)
        url = reverse("todo:create_task")
        data = {"title": "New Task", "description": "New task description"}
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse("todo:task_list")
        assert Task.objects.filter(title="New Task", user=profile).exists()

    def test_task_create_auto_assigns_user(self, client, user, profile):
        """Test that created task is automatically assigned to user's profile"""
        client.force_login(user)
        url = reverse("todo:create_task")
        data = {
            "title": "Auto Assigned Task",
            "description": "This task should be auto-assigned",
        }
        client.post(url, data)
        task = Task.objects.get(title="Auto Assigned Task")
        assert task.user == profile


@pytest.mark.django_db
class TestTaskDetailView:
    """Test suite for TaskDetailView"""

    def test_task_detail_unauthenticated(self, client, task):
        """Test that unauthenticated users are redirected to login"""
        url = reverse("todo:detail_task", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_task_detail_authenticated(self, client, user, task):
        """Test that authenticated users can view their own task details"""
        client.force_login(user)
        url = reverse("todo:detail_task", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["todo"] == task

    def test_task_detail_other_user(self, client, user, another_profile):
        """Test that users cannot view other users' task details"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task",
        )
        client.force_login(user)
        url = reverse("todo:detail_task", kwargs={"pk": other_task.pk})
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestTaskUpdateView:
    """Test suite for TaskUpdateView"""

    def test_task_update_unauthenticated(self, client, task):
        """Test that unauthenticated users are redirected to login"""
        url = reverse("todo:edit_task", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_task_update_get_authenticated(self, client, user, task):
        """Test GET request to update task page"""
        client.force_login(user)
        url = reverse("todo:edit_task", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_task_update_post_authenticated(self, client, user, task):
        """Test POST request to update a task"""
        client.force_login(user)
        url = reverse("todo:edit_task", kwargs={"pk": task.pk})
        data = {"title": "Updated Task", "description": "Updated description"}
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse("todo:task_list")
        task.refresh_from_db()
        assert task.title == "Updated Task"
        assert task.description == "Updated description"

    def test_task_update_other_user(self, client, user, another_profile):
        """Test that users cannot update other users' tasks"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task",
        )
        client.force_login(user)
        url = reverse("todo:edit_task", kwargs={"pk": other_task.pk})
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestTaskDeleteView:
    """Test suite for TaskDeleteView"""

    def test_task_delete_unauthenticated(self, client, task):
        """Test that unauthenticated users are redirected to login"""
        url = reverse("todo:delete_task", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_task_delete_get_authenticated(self, client, user, task):
        """Test GET request to delete task (should work as POST)"""
        client.force_login(user)
        task_id = task.id
        url = reverse("todo:delete_task", kwargs={"pk": task.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse("todo:task_list")
        assert not Task.objects.filter(id=task_id).exists()

    def test_task_delete_post_authenticated(self, client, user, task):
        """Test POST request to delete a task"""
        client.force_login(user)
        task_id = task.id
        url = reverse("todo:delete_task", kwargs={"pk": task.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert response.url == reverse("todo:task_list")
        assert not Task.objects.filter(id=task_id).exists()

    def test_task_delete_other_user(self, client, user, another_profile):
        """Test that users cannot delete other users' tasks"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task",
        )
        client.force_login(user)
        url = reverse("todo:delete_task", kwargs={"pk": other_task.pk})
        response = client.get(url)
        assert response.status_code == 404
        assert Task.objects.filter(id=other_task.id).exists()


@pytest.mark.django_db
class TestTaskToggleView:
    """Test suite for TaskToggleView"""

    def test_task_toggle_unauthenticated(self, client, task):
        """Test that unauthenticated users are redirected to login"""
        url = reverse("todo:toggle_task", kwargs={"pk": task.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_task_toggle_incomplete_to_complete(self, client, user, task):
        """Test toggling an incomplete task to complete"""
        assert task.complete is False
        client.force_login(user)
        url = reverse("todo:toggle_task", kwargs={"pk": task.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert response.url == reverse("todo:task_list")
        task.refresh_from_db()
        assert task.complete is True

    def test_task_toggle_complete_to_incomplete(self, client, user, completed_task):
        """Test toggling a completed task to incomplete"""
        assert completed_task.complete is True
        client.force_login(user)
        url = reverse("todo:toggle_task", kwargs={"pk": completed_task.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert response.url == reverse("todo:task_list")
        completed_task.refresh_from_db()
        assert completed_task.complete is False

    def test_task_toggle_other_user(self, client, user, another_profile):
        """Test that users cannot toggle other users' tasks"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task",
            complete=False,
        )
        client.force_login(user)
        url = reverse("todo:toggle_task", kwargs={"pk": other_task.pk})
        response = client.post(url)
        assert response.status_code == 404
        other_task.refresh_from_db()
        assert other_task.complete is False
