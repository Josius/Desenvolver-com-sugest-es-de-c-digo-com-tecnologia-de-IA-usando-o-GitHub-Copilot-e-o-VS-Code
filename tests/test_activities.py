"""
Tests for Mergington High School API
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for students interested in court sports",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and play tennis with fellow students",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["sophie@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Play instruments and perform in school concerts",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, reset_activities):
        """Should return all activities"""
        # Arrange
        expected_activity_count = 9
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_contains_required_fields(self, reset_activities):
        """Each activity should have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing from {activity_name}"

    def test_get_activities_participants_are_list(self, reset_activities):
        """Participants should be a list"""
        # Arrange - no setup needed, just verify structure
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, reset_activities):
        """Should successfully sign up a new participant"""
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]

    def test_signup_duplicate_email_fails(self, reset_activities):
        """Should not allow duplicate signups"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Should return 404 for non-existent activity"""
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_activities(self, reset_activities):
        """Student should be able to sign up for multiple activities"""
        # Arrange
        email = "student@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class"]
        
        # Act
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            # Assert partial - verify each signup succeeds
            assert response.status_code == 200
        
        # Assert final - verify in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, reset_activities):
        """Should successfully unregister a participant"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]

    def test_unregister_nonexistent_student_fails(self, reset_activities):
        """Should return 400 for non-existent participant"""
        # Arrange
        activity = "Chess Club"
        email = "nonexistent@mergington.edu"  # Not signed up
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Should return 404 for non-existent activity"""
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_all_participants(self, reset_activities):
        """Should be able to remove all participants"""
        # Arrange
        activity = "Chess Club"
        original_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        for email in original_participants:
            response = client.post(
                f"/activities/{activity}/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Assert
        activities_response = client.get("/activities")
        assert len(activities_response.json()[activity]["participants"]) == 0


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_signup_and_unregister_workflow(self, reset_activities):
        """Complete workflow: signup, verify, unregister"""
        # Arrange
        email = "integration@mergington.edu"
        activity = "Programming Class"
        
        # Act - Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert - Signup succeeded
        assert signup_response.status_code == 200
        
        # Act - Verify in list
        get_response = client.get("/activities")
        
        # Assert - Participant is in list
        assert email in get_response.json()[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert - Unregister succeeded
        assert unregister_response.status_code == 200
        
        # Act - Verify removed from list
        final_response = client.get("/activities")
        
        # Assert - Participant is no longer in list
        assert email not in final_response.json()[activity]["participants"]
