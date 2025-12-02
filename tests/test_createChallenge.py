

from datetime import datetime, timedelta
from unittest.mock import patch
from backend.createChallenge import validate_challenge_data, create_challenge
from backend.logWorkout import log_workout, validate_workout_data
from backend.recipeSuggestions.suggest import generate_day_plan
from backend.app import app as flask_app
from backend.data_manager import (
    load_challenges, save_challenges, get_challenge_by_id,
    get_public_challenges, add_challenge, load_workouts,
    save_workouts, get_workout_by_id, add_workout, get_all_activities,
    CHALLENGES_FILE, WORKOUTS_FILE
)

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
import pytest
from backend.recipeSuggestions.suggest import _normalize_list_field, generate_day_plan, RECIPES


def test_normalize_list_field_basic():
    assert _normalize_list_field("eggs, milk,  bread ") == ["eggs", "milk", "bread"]


def test_normalize_list_field_empty():
    assert _normalize_list_field("") == []
    assert _normalize_list_field(None) == []


def test_generate_plan_filters_by_goal():
    result = generate_day_plan(
        goal="Keto",
        diet="No Preference",
        meal_type="Breakfast",
        calorie_target="",
        cooking_time="long",
        have_ingredients="",
        avoid_ingredients=""
    )
    # All returned meals should be keto breakfast recipes
    for recipe in result["meals"]:
        assert "Keto" in recipe["diet"] or "Keto" in recipe["goal"]
        assert recipe["meal_type"] == "Breakfast"


def test_generate_plan_filters_by_avoid():
    result = generate_day_plan(
        goal="No Preference",
        diet="No Preference",
        meal_type="Breakfast",
        calorie_target="",
        cooking_time="long",
        have_ingredients="",
        avoid_ingredients="eggs"
    )
    for recipe in result["meals"]:
        assert "eggs" not in recipe["ingredients"]


def test_generate_plan_respects_cooking_time():
    result = generate_day_plan(
        goal="No Preference",
        diet="No Preference",
        meal_type="Breakfast",
        calorie_target="",
        cooking_time="quick",   # max 15 min
        have_ingredients="",
        avoid_ingredients=""
    )
    for recipe in result["meals"]:
        assert recipe["cook_time_min"] <= 15


def test_generate_plan_specific_meal_type():
    result = generate_day_plan(
        goal="No Preference",
        diet="No Preference",
        meal_type="Lunch",
        calorie_target="",
        cooking_time="long",
        have_ingredients="",
        avoid_ingredients=""
    )
    for recipe in result["meals"]:
        assert recipe["meal_type"] == "Lunch"


def test_generate_plan_respects_max_daily_calories():
    result = generate_day_plan(
        goal="No Preference",
        diet="No Preference",
        meal_type="",
        calorie_target="",
        cooking_time="long",
        have_ingredients="",
        avoid_ingredients="",
        max_daily_calories=500
    )
    assert result["total_calories"] <= 500
# backend/test_app.py


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

# ------------------------------
# Test the static routes
# ------------------------------

def test_index(client):
    res = client.get('/')
    assert res.status_code in [200, 404]  # 404 if homepage.html missing

def test_serve_image(client):
    res = client.get('/img/some_image.png')
    assert res.status_code in [200, 404]  # 404 if image missing

def test_serve_static(client):
    res = client.get('/nonexistent_file.js')
    assert res.status_code in [200, 404]

# ------------------------------
# Test API - Challenges
# ------------------------------

def test_get_challenges(client):
    res = client.get('/api/challenges')
    data = res.get_json()
    assert res.status_code == 200
    assert 'success' in data

def test_get_challenges_with_privacy(client):
    res = client.get('/api/challenges?privacy=public')
    data = res.get_json()
    assert res.status_code == 200
    assert 'success' in data

def test_get_challenge_by_id_not_found(client):
    res = client.get('/api/challenges/invalid_id')
    data = res.get_json()
    assert res.status_code == 404
    assert data['success'] is False

# ------------------------------
# Test API - Workouts
# ------------------------------

def test_get_workouts(client):
    res = client.get('/api/workouts')
    data = res.get_json()
    assert res.status_code == 200
    assert 'success' in data

def test_get_workout_by_id_not_found(client):
    res = client.get('/api/workouts/invalid_id')
    data = res.get_json()
    assert res.status_code == 404
    assert data['success'] is False

# ------------------------------
# Test API - Recipe Plan
# ------------------------------

def test_recipe_plan_minimal(client):
    payload = {
        "goal": "Bulking",
        "diet": "Vegetarian",
        "mealType": "Breakfast"
    }
    res = client.post('/api/recipe-plan', data=json.dumps(payload), content_type='application/json')
    data = res.get_json()
    assert res.status_code == 200
    assert 'meals' in data
    assert 'total_calories' in data

def test_recipe_plan_empty(client):
    res = client.post('/api/recipe-plan', data=json.dumps({}), content_type='application/json')
    data = res.get_json()
    assert res.status_code == 200
    assert 'meals' in data
    assert 'total_calories' in data


# backend/test_data_manager.py

# ------------------------------
# Helpers
# ------------------------------
def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# ------------------------------
# Challenge Tests
# ------------------------------
def test_load_and_save_challenges(tmp_path, monkeypatch):
    test_file = tmp_path / "challenges.json"
    monkeypatch.setattr('data_manager.CHALLENGES_FILE', str(test_file))

    # Save challenges
    challenges = [{"id": "1", "name": "Test Challenge", "privacy": "public"}]
    assert save_challenges(challenges) is True

    # Load challenges
    loaded = load_challenges()
    assert loaded == challenges

def test_get_challenge_by_id(tmp_path, monkeypatch):
    test_file = tmp_path / "challenges.json"
    monkeypatch.setattr('data_manager.CHALLENGES_FILE', str(test_file))

    challenges = [
        {"id": "1", "name": "C1", "privacy": "public"},
        {"id": "2", "name": "C2", "privacy": "private"}
    ]
    write_json(test_file, challenges)

    c = get_challenge_by_id("1")
    assert c['name'] == "C1"

    c_none = get_challenge_by_id("nonexistent")
    assert c_none is None

def test_get_public_challenges(tmp_path, monkeypatch):
    test_file = tmp_path / "challenges.json"
    monkeypatch.setattr('data_manager.CHALLENGES_FILE', str(test_file))

    challenges = [
        {"id": "1", "privacy": "public"},
        {"id": "2", "privacy": "private"}
    ]
    write_json(test_file, challenges)

    public = get_public_challenges()
    assert len(public) == 1
    assert public[0]['id'] == "1"

def test_add_challenge(tmp_path, monkeypatch):
    test_file = tmp_path / "challenges.json"
    monkeypatch.setattr('data_manager.CHALLENGES_FILE', str(test_file))

    challenge = {"id": "1", "name": "New Challenge", "privacy": "public"}
    result = add_challenge(challenge)
    assert result is True
    loaded = load_challenges()
    assert loaded[0]['id'] == "1"

# ------------------------------
# Workout Tests
# ------------------------------
def test_load_and_save_workouts(tmp_path, monkeypatch):
    test_file = tmp_path / "workouts.json"
    monkeypatch.setattr('data_manager.WORKOUTS_FILE', str(test_file))

    workouts = [{"id": "w1", "name": "Workout 1"}]
    assert save_workouts(workouts) is True

    loaded = load_workouts()
    assert loaded == workouts

def test_get_workout_by_id(tmp_path, monkeypatch):
    test_file = tmp_path / "workouts.json"
    monkeypatch.setattr('data_manager.WORKOUTS_FILE', str(test_file))

    workouts = [
        {"id": "w1", "name": "Workout1"},
        {"id": "w2", "name": "Workout2"}
    ]
    write_json(test_file, workouts)

    w = get_workout_by_id("w1")
    assert w['name'] == "Workout1"

    w_none = get_workout_by_id("nonexistent")
    assert w_none is None

def test_add_workout(tmp_path, monkeypatch):
    test_file = tmp_path / "workouts.json"
    monkeypatch.setattr('data_manager.WORKOUTS_FILE', str(test_file))

    workout = {"id": "w1", "name": "Workout New"}
    result = add_workout(workout)
    assert result is True
    loaded = load_workouts()
    assert loaded[0]['id'] == "w1"

# ------------------------------
# Combined Activities Test
# ------------------------------
def test_get_all_activities(tmp_path, monkeypatch):
    # Mock both files
    challenges_file = tmp_path / "challenges.json"
    workouts_file = tmp_path / "workouts.json"
    monkeypatch.setattr('data_manager.CHALLENGES_FILE', str(challenges_file))
    monkeypatch.setattr('data_manager.WORKOUTS_FILE', str(workouts_file))

    challenges = [
        {"id": "c1", "privacy": "public", "created_at": "2025-01-01"},
        {"id": "c2", "privacy": "private", "created_at": "2025-01-02"}
    ]
    workouts = [
        {"id": "w1", "created_at": "2025-01-03"},
        {"id": "w2", "created_at": "2025-01-01"}
    ]

    write_json(challenges_file, challenges)
    write_json(workouts_file, workouts)

    all_activities = get_all_activities()
    # Should include public challenges + all workouts
    ids = [a['id'] for a in all_activities]
    assert "c1" in ids
    assert "w1" in ids
    assert "c2" not in ids  # private challenge excluded
