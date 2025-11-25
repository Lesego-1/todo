import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Task

# Test signup
@pytest.mark.django_db
def test_signup_endpoint():
    # Test user signup for the first time
    client = APIClient()
    response = client.post("/signup/", {"username":"User1", "password":"user1234!"}, format="json")
    
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="User1").exists()
    
    # Test duplicate username
    duplicate_response = client.post("/signup/", {"username":"User1", "password":"newPassword1!"}, format="json")
    
    assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

# Test login
@pytest.mark.django_db
def test_login_endpoint():
    user = User.objects.create_user(username="User1", password="User1234!")
    
    client = APIClient()
    
    # Correct credentials
    response = client.post("/login/", {"username": "User1", "password": "User1234!"}, format="json")
    
    assert response.status_code == status.HTTP_200_OK
    
    # Incorrect password
    wrong_response = client.post("/login/", {"username": "User1", "password": "WrongPassword1!"}, format="json")
    
    assert wrong_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # User not found
    wrong_username_response = client.post("/login/", {"username": "User500", "password": "WrongPass12!"}, format="json")
    
    assert wrong_username_response.status_code == status.HTTP_401_UNAUTHORIZED

# Test POST and bad POST
@pytest.mark.django_db
def test_post_endpoint():
    # Test creating a task
    user = User.objects.create_user(username="User1", password="User1234!")
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    task = {
        "title": "Finish Django tests",
        "description": "Write pytest tests for signup, login, and task endpoints",
        "due_date": "2025-12-05",
        "completed": False
    }
    response = client.post("/tasks/", task, format="json")
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Test incomplete data
    incomplete_task = {
        "title": "Water the plants",
        "description": "Water the plants, not the cactus though.",
    }
    incomplete_response = client.post("/tasks/", incomplete_task, format="json")
    
    assert incomplete_response.status_code == status.HTTP_400_BAD_REQUEST

# Test GET
@pytest.mark.django_db
def test_get_endpoint():
    # Test GET endpoint
    user = User.objects.create_user(username="User1", password="User1234!")
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.get("/tasks/")
    
    assert response.status_code == status.HTTP_200_OK

# Test PUT and bad PUT
@pytest.mark.django_db
def test_put_endpoint():
    # Test Updating tasks
    user = User.objects.create_user(username="User1", password="User1234!")
    client = APIClient()
    client.force_authenticate(user=user)
    
    task = Task.objects.create(
        title="Intial Title",
        description="Intial Description",
        due_date = "2025-12-05",
        user=user
    )
    
    updated_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "due_date": "2025-12-15",
        "completed": True
    }
    
    response = client.put(f"/tasks/{task.id}/", updated_data, format="json")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == updated_data["title"]
    assert response.data["completed"] is True
    
# Test DELETE and non existent task
@pytest.mark.django_db
def test_delete_endpoint():
    user = User.objects.create_user(username="User1", password="User1234!")
    client = APIClient()
    client.force_authenticate(user=user)
    
    task = Task.objects.create(
        title="Title",
        description="Description",
        due_date = "2025-12-05",
        user=user
    )
    
    response = client.delete(f"/tasks/{task.id}/")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Test deleting a task that does not exist
    wrong_response = client.delete("/tasks/5000/")
    
    assert wrong_response.status_code == status.HTTP_404_NOT_FOUND

# Test Filtering and filtering non existent filters
@pytest.mark.django_db
def test_filtering_requests():
    user = User.objects.create_user(username="User1", password="User1234!")
    client = APIClient()
    client.force_authenticate(user=user)
    
    Task.objects.create(title="Task 1", description="Desc 1", due_date="2025-12-01", completed=True, user=user)
    Task.objects.create(title="Task 2", description="Desc 2", due_date="2025-12-02", completed=False, user=user)
    
    # Filter by completed tasks
    response = client.get("/tasks/?completed=True")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

# Test Pagination and 0 or negative pages or beyond the pages
@pytest.mark.django_db
def test_pagination_requests():
    user = User.objects.create_user(username="User1", password="User1234!")
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Create 5 tasks
    for i in range(1, 26):
        if i < 10:
            Task.objects.create(
                title=f"Task {i}",
                description=f"Desc {i}",
                due_date=f"2025-12-0{i}",
                completed=False,
                user=user
            )
        else:
            Task.objects.create(
                title=f"Task {i}",
                description=f"Desc {i}",
                due_date=f"2025-12-{i}",
                completed=False,
                user=user
            )
    
    # Request first page
    response = client.get("/tasks/?page=1")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 12
    
    response = client.get("/tasks/?page=2")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 12
    
    response = client.get("/tasks/?page=3")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    
    # Test for non existent page
    response = client.get("/tasks/?page=10")
    assert response.status_code == status.HTTP_404_NOT_FOUND