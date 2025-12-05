"""
FastAPI tests for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
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
            "description": "Competitive basketball team and training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Join our student orchestra and perform in concerts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation skills and compete in debate competitions",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM topics",
            "schedule": "Mondays and Fridays, 3:45 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_participants_data(self, client, reset_activities):
        """Test that participants are correctly returned"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_updates_participant_count(self, client, reset_activities):
        """Test that signup updates participant list"""
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Programming Class"]["participants"])
        
        # Signup
        client.post(
            "/activities/Programming%20Class/signup?email=testuser@mergington.edu",
            follow_redirects=True
        )
        
        # Check new count
        updated_response = client.get("/activities")
        new_count = len(updated_response.json()["Programming Class"]["participants"])
        
        assert new_count == initial_count + 1


class TestUnregister:
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister for student not registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_reduces_participant_count(self, client, reset_activities):
        """Test that unregister reduces participant count"""
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Unregister
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        
        # Check new count
        updated_response = client.get("/activities")
        new_count = len(updated_response.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count - 1


class TestIntegration:
    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Test complete flow of signup and then unregister"""
        email = "integration@mergington.edu"
        activity = "Basketball%20Team"
        
        # Initial state
        response = client.get("/activities")
        initial = len(response.json()["Basketball Team"]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=True
        )
        assert signup_response.status_code == 200
        
        # Check increased count
        response = client.get("/activities")
        after_signup = len(response.json()["Basketball Team"]["participants"])
        assert after_signup == initial + 1
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}",
            follow_redirects=True
        )
        assert unregister_response.status_code == 200
        
        # Check back to initial count
        response = client.get("/activities")
        final = len(response.json()["Basketball Team"]["participants"])
        assert final == initial

    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple students signing up and unregistering"""
        activity = "Tennis%20Club"
        students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # All sign up
        for student in students:
            response = client.post(
                f"/activities/{activity}/signup?email={student}",
                follow_redirects=True
            )
            assert response.status_code == 200
        
        # Check all are added
        response = client.get("/activities")
        current_count = len(response.json()["Tennis Club"]["participants"])
        assert current_count == initial_count + 3
        
        # Unregister first two
        for student in students[:2]:
            response = client.post(
                f"/activities/{activity}/unregister?email={student}",
                follow_redirects=True
            )
            assert response.status_code == 200
        
        # Check count decreased
        response = client.get("/activities")
        final_count = len(response.json()["Tennis Club"]["participants"])
        assert final_count == initial_count + 1
        assert students[2] in response.json()["Tennis Club"]["participants"]
