"""
Pytest configuration and fixtures for FastAPI application tests.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient with a fresh app instance.
    Resets the activities database to initial state before each test.
    """
    # Reset activities to initial state
    activities.clear()
    activities.update({
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
        "Soccer Team": {
            "description": "Train for matches and build teamwork on the field",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice ball handling, shooting, and team strategies",
            "schedule": "Tuesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "mason@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore drawing, painting, and mixed media art",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Develop acting skills and perform plays for the school",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["harper@mergington.edu", "elijah@mergington.edu"]
        },
        "Robotics Workshop": {
            "description": "Design and build robots while learning engineering concepts",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["charlotte@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Research current topics and practice public speaking",
            "schedule": "Mondays and Wednesdays, 3:45 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["amelia@mergington.edu", "henry@mergington.edu"]
        }
    })
    
    return TestClient(app)
