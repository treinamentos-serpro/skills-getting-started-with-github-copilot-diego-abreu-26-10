import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "description": "Practice chess",
                "schedule": "Fridays",
                "max_participants": 3,
                "participants": ["existing@example.com"],
            }
        },
    )

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = {
        "description": "Practice chess",
        "schedule": "Fridays",
        "max_participants": 3,
        "participants": ["existing@example.com"],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"Chess Club": expected_activity}


def test_signup_adds_participant(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.com for Chess Club"}
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == [
        "existing@example.com",
        email,
    ]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_requires_email(client):
    # Arrange
    url = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_unregister_removes_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.com from Chess Club"
    }
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "unknown@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }