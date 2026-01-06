import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from accounts.models import User, Profile
from todo.models import Task
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    """Create a verified user for testing"""
    user = User.objects.create_user(
        email="testuser@example.com",
        password="testpass123",
        is_verified=True
    )
    return user


@pytest.fixture
def another_user(db):
    """Create another verified user for testing"""
    user = User.objects.create_user(
        email="anotheruser@example.com",
        password="testpass123",
        is_verified=True
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
def authenticated_client(user):
    """Create an authenticated API client"""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def another_authenticated_client(another_user):
    """Create an authenticated API client for another user"""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=another_user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def task(profile):
    """Create a task for testing"""
    return Task.objects.create(
        user=profile,
        title="Test Task",
        description="This is a test task description",
        complete=False
    )


@pytest.fixture
def completed_task(profile):
    """Create a completed task for testing"""
    return Task.objects.create(
        user=profile,
        title="Completed Task",
        description="This is a completed task",
        complete=True
    )


@pytest.mark.django_db
class TestTaskModelViewSet:
    """Test suite for TaskModelViewSet API"""

    def test_list_tasks_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list tasks"""
        url = reverse("todo:api-v1:task-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tasks_authenticated(self, authenticated_client, task, completed_task):
        """Test that authenticated users can list their own tasks"""
        url = reverse("todo:api-v1:task-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_objects"] == 2
        assert len(response.data["results"]) == 2

    def test_list_tasks_only_own_tasks(self, authenticated_client, another_authenticated_client, profile, another_profile):
        """Test that users can only see their own tasks"""
        # Create a task for another user
        another_task = Task.objects.create(
            user=another_profile,
            title="Another User Task",
            description="This is another user's task"
        )
        
        url = reverse("todo:api-v1:task-list")
        
        # Collect all task IDs from all pages
        all_task_ids = []
        page = 1
        while True:
            response = authenticated_client.get(url, {"page": page})
            assert response.status_code == status.HTTP_200_OK
            
            page_task_ids = [t["id"] for t in response.data["results"]]
            all_task_ids.extend(page_task_ids)
            
            # Check if there's a next page
            if not response.data["links"]["next"]:
                break
            page += 1
        
        # Verify that another_task is NOT in the results (main test)
        assert another_task.id not in all_task_ids
        
        # Verify that all returned tasks belong to the authenticated user
        for task_id in all_task_ids:
            task_obj = Task.objects.get(id=task_id)
            assert task_obj.user == profile, f"Task {task_id} belongs to {task_obj.user} but should belong to {profile}"

    def test_create_task_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create tasks"""
        url = reverse("todo:api-v1:task-list")
        data = {
            "title": "New Task",
            "description": "New task description"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_task_authenticated(self, authenticated_client, profile):
        """Test that authenticated users can create tasks"""
        url = reverse("todo:api-v1:task-list")
        data = {
            "title": "New Task",
            "description": "New task description"
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Task"
        # Description may or may not be in response depending on serializer logic
        # But we verify it was saved correctly
        assert response.data["complete"] is False
        assert response.data["user"] == profile.id
        created_task = Task.objects.get(title="New Task")
        assert created_task.description == "New task description"

    def test_create_task_without_description(self, authenticated_client, profile):
        """Test creating a task without description"""
        url = reverse("todo:api-v1:task-list")
        data = {
            "title": "Task Without Description"
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Task Without Description"
        # Verify it was saved correctly
        created_task = Task.objects.get(title="Task Without Description")
        assert created_task.description == ""

    def test_retrieve_task_unauthenticated(self, api_client, task):
        """Test that unauthenticated users cannot retrieve tasks"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_task_authenticated(self, authenticated_client, task):
        """Test that authenticated users can retrieve their own tasks"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == task.id
        assert response.data["title"] == task.title
        assert response.data["description"] == task.description
        # Detail view should not have snippet, relative_url, absolute_url
        assert "snippet" not in response.data
        assert "relative_url" not in response.data
        assert "absolute_url" not in response.data

    def test_retrieve_task_other_user(self, authenticated_client, another_profile):
        """Test that users cannot retrieve other users' tasks"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task"
        )
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": other_task.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task_unauthenticated(self, api_client, task):
        """Test that unauthenticated users cannot update tasks"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        data = {
            "title": "Updated Task",
            "description": "Updated description"
        }
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_task_authenticated(self, authenticated_client, task):
        """Test that authenticated users can update their own tasks"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        data = {
            "title": "Updated Task",
            "description": "Updated description"
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Task"
        assert response.data["description"] == "Updated description"
        task.refresh_from_db()
        assert task.title == "Updated Task"
        assert task.description == "Updated description"

    def test_partial_update_task(self, authenticated_client, task):
        """Test partial update of a task"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        data = {"title": "Partially Updated Task"}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Partially Updated Task"
        task.refresh_from_db()
        assert task.title == "Partially Updated Task"
        # Description should remain unchanged
        assert task.description == "This is a test task description"

    def test_update_task_complete_status(self, authenticated_client, task):
        """Test updating task completion status"""
        assert task.complete is False
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        data = {"complete": True}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["complete"] is True
        task.refresh_from_db()
        assert task.complete is True

    def test_update_task_other_user(self, authenticated_client, another_profile):
        """Test that users cannot update other users' tasks"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task"
        )
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": other_task.pk})
        data = {"title": "Hacked Task"}
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_unauthenticated(self, api_client, task):
        """Test that unauthenticated users cannot delete tasks"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_task_authenticated(self, authenticated_client, task):
        """Test that authenticated users can delete their own tasks"""
        task_id = task.id
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task_id).exists()

    def test_delete_task_other_user(self, authenticated_client, another_profile):
        """Test that users cannot delete other users' tasks"""
        other_task = Task.objects.create(
            user=another_profile,
            title="Other User Task",
            description="Other user's task"
        )
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": other_task.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Task.objects.filter(id=other_task.id).exists()

    def test_task_user_read_only(self, authenticated_client, task, another_profile):
        """Test that user field is read-only"""
        url = reverse("todo:api-v1:task-detail", kwargs={"pk": task.pk})
        data = {
            "title": "Test",
            "user": another_profile.id
        }
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        # User should remain unchanged
        task.refresh_from_db()
        assert task.user != another_profile

    def test_list_tasks_with_snippet(self, authenticated_client, task):
        """Test that list view includes snippet field"""
        url = reverse("todo:api-v1:task-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0
        task_data = response.data["results"][0]
        assert "snippet" in task_data
        assert "relative_url" in task_data
        assert "absolute_url" in task_data
        # Description should not be in list view
        assert "description" not in task_data

    def test_task_snippet_content(self, authenticated_client, task):
        """Test that snippet returns first 5 characters of description"""
        url = reverse("todo:api-v1:task-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        task_data = response.data["results"][0]
        assert task_data["snippet"] == task.description[:5]


@pytest.mark.django_db
class TestTaskFilteringAndSearch:
    """Test suite for Task filtering, search, and ordering"""

    def test_filter_by_complete_status(self, authenticated_client, task, completed_task):
        """Test filtering tasks by complete status"""
        url = reverse("todo:api-v1:task-list")
        # Filter completed tasks
        response = authenticated_client.get(url, {"complete": "true"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_objects"] == 1
        assert response.data["results"][0]["complete"] is True
        
        # Filter incomplete tasks
        response = authenticated_client.get(url, {"complete": "false"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_objects"] == 1
        assert response.data["results"][0]["complete"] is False

    def test_search_by_title(self, authenticated_client, profile):
        """Test searching tasks by title"""
        Task.objects.create(
            user=profile,
            title="Python Task",
            description="Learn Python"
        )
        Task.objects.create(
            user=profile,
            title="Django Task",
            description="Learn Django"
        )
        
        url = reverse("todo:api-v1:task-list")
        response = authenticated_client.get(url, {"search": "Python"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_objects"] == 1
        assert "Python" in response.data["results"][0]["title"]

    def test_search_by_description(self, authenticated_client, profile):
        """Test searching tasks by description"""
        task1 = Task.objects.create(
            user=profile,
            title="Task 1",
            description="Learn Python programming"
        )
        Task.objects.create(
            user=profile,
            title="Task 2",
            description="Learn Django framework"
        )
        
        url = reverse("todo:api-v1:task-list")
        response = authenticated_client.get(url, {"search": "Python"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_objects"] == 1
        # In list view, description is not shown, but search works on it
        # We verify by checking the task ID matches
        assert response.data["results"][0]["id"] == task1.id
        # Snippet should contain first 5 chars of description
        assert response.data["results"][0]["snippet"] == "Learn"

    def test_ordering_by_created_date(self, authenticated_client, profile):
        """Test ordering tasks by created_date"""
        task1 = Task.objects.create(
            user=profile,
            title="First Task",
            description="First"
        )
        task2 = Task.objects.create(
            user=profile,
            title="Second Task",
            description="Second"
        )
        
        url = reverse("todo:api-v1:task-list")
        # Order by created_date ascending
        response = authenticated_client.get(url, {"ordering": "created_date"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == task1.id
        assert response.data["results"][1]["id"] == task2.id
        
        # Order by created_date descending
        response = authenticated_client.get(url, {"ordering": "-created_date"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == task2.id
        assert response.data["results"][1]["id"] == task1.id

    def test_pagination(self, authenticated_client, profile):
        """Test that pagination works correctly"""
        # Create more than one page of tasks
        for i in range(15):
            Task.objects.create(
                user=profile,
                title=f"Task {i}",
                description=f"Description {i}"
            )
        
        url = reverse("todo:api-v1:task-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "total_objects" in response.data
        assert "total_pages" in response.data
        assert "links" in response.data
        assert "next" in response.data["links"]
        assert "previous" in response.data["links"]
        assert "results" in response.data
        assert response.data["total_objects"] == 15
        assert response.data["total_pages"] > 1

