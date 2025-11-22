

from datetime import datetime, timedelta
from unittest.mock import patch
from backend.createChallenge import validate_challenge_data, create_challenge
from backend.logWorkout import log_workout, validate_workout_data


# ---------- VALIDATION TESTS ----------

def test_validation_success():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    data = {
        "title": "Morning Run Challenge",
        "goal": "Run every morning for 7 days",
        "start_date": tomorrow,
        "end_date": next_week,
        "description": "A fun challenge to stay consistent with morning workouts!",
        "privacy": "public"
    }

    valid, errors = validate_challenge_data(data)
    assert valid is True
    assert errors == []


def test_missing_title():
    data = {
        "title": "",
        "goal": "Test",
        "start_date": "2025-01-01",
        "end_date": "2025-01-02",
        "description": "Valid desc",
        "privacy": "private"
    }
    valid, errors = validate_challenge_data(data)
    assert valid is False
    assert "Challenge title is required" in errors


def test_title_too_long():
    data = {
        "title": "A" * 101,
        "goal": "Goal text",
        "start_date": "2030-01-01",
        "end_date": "2030-01-02",
        "description": "Valid description",
        "privacy": "public"
    }
    valid, errors = validate_challenge_data(data)
    assert valid is False
    assert "Challenge title must be less than 100 characters" in errors


def test_start_date_in_past():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    data = {
        "title": "Test",
        "goal": "Goal",
        "start_date": yesterday,
        "end_date": tomorrow,
        "description": "Long enough description",
        "privacy": "public"
    }

    valid, errors = validate_challenge_data(data)
    assert valid is False
    assert "Start date cannot be in the past" in errors


def test_end_date_before_start_date():
    today = datetime.now().strftime("%Y-%m-%d")

    data = {
        "title": "Test",
        "goal": "Goal",
        "start_date": today,
        "end_date": today,
        "description": "Long enough description",
        "privacy": "public"
    }

    valid, errors = validate_challenge_data(data)
    assert valid is False
    assert "End date must be after start date" in errors


def test_invalid_privacy():
    data = {
        "title": "Test",
        "goal": "Goal",
        "start_date": "2030-01-01",
        "end_date": "2030-01-02",
        "description": "Valid description",
        "privacy": "friends-only"
    }

    valid, errors = validate_challenge_data(data)
    assert valid is False
    assert "Privacy setting is required (private or public)" in errors


# ---------- CREATE CHALLENGE TESTS ----------

@patch("backend.createChallenge.add_challenge", return_value=True)

def test_create_challenge_success(mock_add):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    data = {
        "title": "My Challenge",
        "goal": "Do something great",
        "start_date": tomorrow,
        "end_date": next_week,
        "description": "A valid description indeed!",
        "privacy": "private",
        "invited_friends": ["friend1"]
    }

    success, response, status = create_challenge(data)

    assert success is True
    assert response["success"] is True
    assert "challenge" in response
    assert status == 201
    mock_add.assert_called_once()


@patch("createChallenge.add_challenge", return_value=False)
def test_create_challenge_save_failure(mock_add):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    data = {
        "title": "My Challenge",
        "goal": "Do something great",
        "start_date": tomorrow,
        "end_date": next_week,
        "description": "Valid description content",
        "privacy": "public"
    }

    success, response, status = create_challenge(data)

    assert success is False
    assert response["success"] is False
    assert "Failed to save challenge" in response["errors"]
    assert status == 500


def test_create_challenge_validation_failure():
    data = {
        "title": "",
        "goal": "",
        "start_date": "",
        "end_date": "",
        "description": "",
        "privacy": ""
    }

    success, response, status = create_challenge(data)

    assert success is False
    assert response["success"] is False
    assert len(response["errors"]) > 0
    assert status == 400

# tests/test_log_workout.py

# Sample valid workout data
valid_data = {
    "workout_name": "Morning Run",
    "date": "2025-11-21",
    "duration": "60",
    "workout_type": "cardio",
    "intensity": "medium",
    "notes": "Felt good",
    "calories": "500"
}

# Invalid workout data (missing fields)
invalid_data = {
    "workout_name": "",
    "date": "2025-11-21",
    "duration": "60",
    "workout_type": "unknown",
    "intensity": "extreme",
    "notes": "Bad",
    "calories": "-50"
}

def test_validate_workout_data_success():
    is_valid, errors = validate_workout_data(valid_data)
    assert is_valid
    assert errors == []

def test_validate_workout_data_failure():
    is_valid, errors = validate_workout_data(invalid_data)
    assert not is_valid
    assert len(errors) >= 4  # Expect multiple validation errors

@patch("backend.logWorkout.add_workout", return_value=True)
def test_log_workout_success(mock_add):
    success, response, status = log_workout(valid_data)
    mock_add.assert_called_once()
    assert success
    assert response["success"] is True
    assert status == 201
    assert "workout" in response

@patch("backend.logWorkout.add_workout", return_value=False)
def test_log_workout_save_failure(mock_add):
    success, response, status = log_workout(valid_data)
    mock_add.assert_called_once()
    assert not success
    assert response["success"] is False
    assert status == 500
    assert "Failed to save workout" in response["errors"]

def test_log_workout_validation_failure():
    success, response, status = log_workout(invalid_data)
    assert not success
    assert response["success"] is False
    assert status == 400
    assert len(response["errors"]) >= 4
