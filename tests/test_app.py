"""
FastAPI backend tests using AAA (Arrange-Act-Assert) pattern.

Tests cover all endpoints: GET activities, POST signup, DELETE unregister.
"""

import pytest


class TestGetActivities:
    """Test GET /activities endpoint."""

    def test_get_all_activities_success(self, client):
        """Test successful retrieval of all activities."""
        # Arrange - No special setup needed, using fixture data

        # Act - Make GET request to activities endpoint
        response = client.get("/activities")

        # Assert - Check response status and structure
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 3  # Chess Club, Programming Class, Gym Class

        # Check that each activity has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_participant(self, client):
        """Test successful signup of a new participant."""
        # Arrange - Prepare test data
        activity_name = "Chess Club"
        new_email = "test@mergington.edu"

        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act - Attempt to sign up the new participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert - Check successful response
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert new_email in result["message"]
        assert activity_name in result["message"]

        # Verify participant was added to the activity
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert new_email in updated_participants

    def test_signup_duplicate_participant(self, client):
        """Test signup failure when participant is already registered."""
        # Arrange - Use an email that's already in Chess Club
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already exists

        # Act - Attempt to sign up the duplicate participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )

        # Assert - Check error response
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_invalid_activity(self, client):
        """Test signup failure for non-existent activity."""
        # Arrange - Use a non-existent activity name
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"

        # Act - Attempt to sign up for invalid activity
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert - Check 404 error response
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()


class TestUnregister:
    """Test DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_valid_participant(self, client):
        """Test successful unregistration of an existing participant."""
        # Arrange - Use an email that's already in Programming Class
        activity_name = "Programming Class"
        email_to_remove = "emma@mergington.edu"

        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act - Attempt to unregister the participant
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert - Check successful response
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email_to_remove in result["message"]
        assert activity_name in result["message"]

        # Verify participant was removed from the activity
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert email_to_remove not in updated_participants

    def test_unregister_participant_not_found(self, client):
        """Test unregister failure when participant is not in the activity."""
        # Arrange - Use an email that's not in any activity
        activity_name = "Chess Club"
        non_existent_email = "notfound@mergington.edu"

        # Act - Attempt to unregister non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": non_existent_email}
        )

        # Assert - Check 404 error response
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_unregister_invalid_activity(self, client):
        """Test unregister failure for non-existent activity."""
        # Arrange - Use a non-existent activity name
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"

        # Act - Attempt to unregister from invalid activity
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )

        # Assert - Check 404 error response
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()