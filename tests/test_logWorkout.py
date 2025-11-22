# tests/test_log_workout.py

import pytest
from unittest.mock import patch
from backend.logWorkout import log_workout, validate_workout_data

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

@patch("backend.log_workout.add_workout", return_value=True)
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
