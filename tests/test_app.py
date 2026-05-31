import copy

from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)


client = TestClient(app)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_success():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity}/signup"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "missingstudent@mergington.edu"
    url = f"/activities/{activity}/signup"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
