from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_returns_participants(client):
    # Arrange
    expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity = "UnknownClub"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": "new.student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity = "UnknownClub"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
