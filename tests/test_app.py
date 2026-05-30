import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_activity_name in data
    assert "participants" in data[expected_activity_name]
    assert isinstance(data[expected_activity_name]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"
    signup_url = f"/activities/Chess%20Club/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"
    signup_url = f"/activities/Chess%20Club/signup?email={email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_activity_not_found_returns_404(client):
    # Arrange
    signup_url = "/activities/Nonexistent/signup?email=test@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_when_activity_full_returns_400(client):
    # Arrange
    activity = activities["Chess Club"]
    activity["participants"] = [f"user{i}@mergington.edu" for i in range(activity["max_participants"])]
    signup_url = "/activities/Chess%20Club/signup?email=overflow@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    unregister_url = f"/activities/Chess%20Club/unregister?email={email}"

    # Act
    response = client.post(unregister_url)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_registered_returns_400(client):
    # Arrange
    unregister_url = "/activities/Chess%20Club/unregister?email=unknown@mergington.edu"

    # Act
    response = client.post(unregister_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_unregister_activity_not_found_returns_404(client):
    # Arrange
    unregister_url = "/activities/DoesNotExist/unregister?email=test@mergington.edu"

    # Act
    response = client.post(unregister_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"