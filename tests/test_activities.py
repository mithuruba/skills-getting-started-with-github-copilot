"""
Tests for the High School Management System FastAPI application.

Covers all endpoints:
- GET / (root redirect)
- GET /activities (list all activities)
- POST /activities/{activity_name}/signup (student signup)
- DELETE /activities/{activity_name}/participants (student removal)
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint GET /"""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all 9 activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Soccer Team" in activities
        assert "Basketball Club" in activities
        assert "Art Studio" in activities
        assert "Drama Club" in activities
        assert "Robotics Workshop" in activities
        assert "Debate Team" in activities

    def test_activity_response_has_required_fields(self, client):
        """Test that each activity has description, schedule, max_participants, and participants"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_activities_have_initial_participants(self, client):
        """Test that activities have their initial participants"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        # Chess Club starts with 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was added
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_duplicate_signup_returns_400(self, client):
        """Test that signing up the same student twice returns 400"""
        # First signup should succeed
        response1 = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response2.status_code == 400
        
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_already_participating_student_returns_400(self, client):
        """Test that a student who is already in activity cannot signup again"""
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_at_capacity_returns_400(self, client):
        """Test that signup fails when activity is at max capacity"""
        # Create a test activity with very low capacity
        # We'll use Debate Team which has max 14 and 2 initial participants
        # Add 12 more to reach capacity
        for i in range(12):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/Debate Team/signup?email={email}")
            assert response.status_code == 200
        
        # Now activity should be at capacity (14 participants)
        # Attempt to signup one more should fail
        response = client.post("/activities/Debate Team/signup?email=overflow@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "maximum capacity" in data["detail"]

    def test_signup_works_up_to_max_capacity(self, client):
        """Test that we can signup students up to max capacity"""
        # Programming Class has max 20 and 2 initial participants
        # We should be able to add 18 more
        for i in range(18):
            email = f"progstudent{i}@mergington.edu"
            response = client.post(f"/activities/Programming Class/signup?email={email}")
            assert response.status_code == 200
        
        # Verify the activity now has 20 participants (2 initial + 18 new)
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert len(activities["Programming Class"]["participants"]) == 20


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First verify participant is there
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Unregister the participant
        response = client.delete("/activities/Chess Club/participants?email=michael@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
        # Verify the participant was removed
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete("/activities/Nonexistent Club/participants?email=student@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregistering a non-participant returns 404"""
        response = client.delete("/activities/Chess Club/participants?email=notamember@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_participant_not_in_activity_returns_404(self, client):
        """Test that unregistering someone from wrong activity returns 404"""
        # michael@mergington.edu is in Chess Club, not in Programming Class
        response = client.delete("/activities/Programming Class/participants?email=michael@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_then_re_register(self, client):
        """Test that a student can unregister and then sign up again"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Unregister
        unreg_response = client.delete(f"/activities/{activity}/participants?email={email}")
        assert unreg_response.status_code == 200
        
        # Sign up again should work
        signup2_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup2_response.status_code == 200
        
        # Verify participant is in activity
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert email in activities[activity]["participants"]


class TestActivityCapacityEdgeCases:
    """Tests for edge cases related to activity capacity"""

    def test_max_capacity_validation_across_multiple_signups(self, client):
        """Test that capacity is respected across multiple signup requests"""
        # Art Studio has max 15 and 2 initial participants
        # Should be able to add 13 more, but not 14
        
        # Add 13 participants successfully
        for i in range(13):
            email = f"artstudent{i}@mergington.edu"
            response = client.post(f"/activities/Art Studio/signup?email={email}")
            assert response.status_code == 200, f"Failed to signup student {i}"
        
        # Verify we now have 15 participants
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert len(activities["Art Studio"]["participants"]) == 15
        
        # 16th attempt should fail
        response = client.post("/activities/Art Studio/signup?email=overflow@mergington.edu")
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]

    def test_capacity_with_small_max_participants(self, client):
        """Test capacity enforcement with very restrictive limits"""
        # Debate Team has max 14 and 2 initial participants
        # Add 12 more to reach exactly 14
        for i in range(12):
            response = client.post(f"/activities/Debate Team/signup?email=debate{i}@mergington.edu")
            assert response.status_code == 200
        
        # Next signup should fail
        response = client.post("/activities/Debate Team/signup?email=debate_overflow@mergington.edu")
        assert response.status_code == 400

    def test_large_capacity_activity(self, client):
        """Test that large capacity activities can accept many signups"""
        # Gym Class has max 30 and 2 initial participants
        # Should be able to add 28 more
        for i in range(28):
            response = client.post(f"/activities/Gym Class/signup?email=gym{i}@mergington.edu")
            assert response.status_code == 200
        
        # Verify all 30 are there
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert len(activities["Gym Class"]["participants"]) == 30
