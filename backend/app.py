# Spotter Backend Application
from dotenv import load_dotenv 
load_dotenv()
from data_manager import (load_challenges, get_public_challenges, get_challenge_by_id, load_workouts, get_workout_by_id, get_all_activities, get_user_activities)  # Add get_user_activities

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from functools import wraps

# Auth imports
from auth import register_user, login_user, validate_token, logout_user

# Other imports
from recipeSuggestions.suggest import generate_day_plan
from create_Challenge import create_challenge
from logWorkout import log_workout
from data_manager import (load_challenges, get_public_challenges, get_challenge_by_id, load_workouts, get_workout_by_id, get_all_activities)
from getExercises import (generate_exercises, list_muscles_for_body_parts, NoBodyPartsSelected, NoMusclesSelected, InvalidMuscleSelection)
from findClasses import find_classes

# Get the path to the frontend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # project root
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')  # project_root/frontend
IMG_DIR = os.path.join(PROJECT_ROOT, 'img')  # project_root/img

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)


# Authentication Middleware
def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]  # Remove 'Bearer ' prefix
        
        is_valid, email = validate_token(token)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token. Please log in again."
            }), 401
        
        # Add email to request context
        request.user_email = email
        return f(*args, **kwargs)
    
    return decorated_function


# Static File Routes
@app.route('/')
def index():
    """Serve the login page first"""
    try:
        return send_from_directory(app.static_folder, 'login.html')
    except Exception as e:
        print(f"Error serving login page: {e}")
        return f"Error: {e}", 500


@app.route('/img/<path:filename>')
def serve_image(filename):
    """Serve images from the img directory"""
    try:
        return send_from_directory(IMG_DIR, filename)
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        return f"Image not found: {filename}", 404


@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        print(f"Error serving {path}: {e}")
        return f"File not found: {path}", 404


# Authentication Routes
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    success, result, status_code = register_user(email, password)
    return jsonify(result), status_code


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    success, result, status_code = login_user(email, password)
    return jsonify(result), status_code


@app.route("/api/logout", methods=["POST"])
@require_auth
def api_logout():
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
    
    success, result, status_code = logout_user(token)
    return jsonify(result), status_code


@app.route("/api/verify", methods=["GET"])
def api_verify():
    """Verify if a token is still valid"""
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
    
    is_valid, email = validate_token(token)
    if is_valid:
        return jsonify({
            "success": True,
            "email": email
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "Invalid token"
        }), 401


# Challenge Routes (Protected)
@app.route("/api/create_challenge", methods=["POST"])
@require_auth
def api_create_challenge():
    """Create a new challenge"""
    data = request.get_json()
    # Pass the authenticated user's email to create_challenge
    success, result, status_code = create_challenge(data, creator_email=request.user_email)
    return jsonify(result), status_code


@app.route("/api/challenges", methods=["GET"])
@require_auth
def api_get_challenges():
    """Get all challenges"""
    try:
        privacy_filter = request.args.get('privacy')
        
        if privacy_filter:
            challenges = [c for c in load_challenges() if c.get('privacy') == privacy_filter]
        else:
            challenges = load_challenges()
        
        return jsonify({
            "success": True,
            "challenges": challenges
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


@app.route("/api/challenges/<challenge_id>", methods=["GET"])
@require_auth
def api_get_challenge(challenge_id):
    """Get a specific challenge by ID"""
    try:
        challenge = get_challenge_by_id(challenge_id)
        
        if not challenge:
            return jsonify({
                "success": False,
                "errors": ["Challenge not found"]
            }), 404
        
        return jsonify({
            "success": True,
            "challenge": challenge
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


# Workout Routes (Protected)
@app.route("/api/log_workout", methods=["POST"])
@require_auth
def api_log_workout():
    """Log a new workout"""
    data = request.get_json()
    # Pass the authenticated user's email to log_workout
    success, result, status_code = log_workout(data, creator_email=request.user_email)
    return jsonify(result), status_code


@app.route("/api/workouts", methods=["GET"])
@require_auth
def api_get_workouts():
    """Get all workouts"""
    try:
        workouts = load_workouts()
        
        return jsonify({
            "success": True,
            "workouts": workouts
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


@app.route("/api/workouts/<workout_id>", methods=["GET"])
@require_auth
def api_get_workout(workout_id):
    """Get a specific workout by ID"""
    try:
        workout = get_workout_by_id(workout_id)
        
        if not workout:
            return jsonify({
                "success": False,
                "errors": ["Workout not found"]
            }), 404
        
        return jsonify({
            "success": True,
            "workout": workout
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


# Activity Feed Route (Protected)
@app.route("/api/activities", methods=["GET"])
@require_auth
def api_get_activities():
    """Get all activities for the feed"""
    try:
        # Get filter parameter - 'all' for public feed, 'mine' for user's own posts
        feed_type = request.args.get('type', 'all')
        
        if feed_type == 'mine':
            # Get only the current user's activities (both public and private)
            activities = get_user_activities(request.user_email)
        else:
            # Get all public activities
            activities = get_all_activities()
        
        return jsonify({
            "success": True,
            "activities": activities
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


# Recipe Generation Route (Protected)
@app.route("/api/recipe-plan", methods=["POST"])
@require_auth
def recipe_plan():
    data = request.get_json() or {}
    print("Incoming recipe request:", data)

    try:
        plan = generate_day_plan(
            goal=data.get("goal"),
            diet=data.get("diet"),
            meal_type=data.get("mealType"),
            calorie_target=data.get("calorieTarget"),
            cooking_time=data.get("cookingTime"),
            have_ingredients=data.get("ingredients"),
            avoid_ingredients=data.get("allergies"),
        )
        print("Generated plan:", plan)
        return jsonify(plan), 200
    except Exception as e:
        import traceback
        print("ERROR in /api/recipe-plan:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Exercise Generation Routes (Protected)
@app.route("/api/generate_exercises", methods=["POST"])
@require_auth
def api_generate_exercises():
    """Generate exercises based on selected body parts and muscles"""
    data = request.get_json() or {}
    body_parts = data.get("bodyParts", [])
    muscles = data.get("muscles", [])

    try:
        results = generate_exercises(body_parts, muscles)
        return jsonify({
            "success": True,
            "exercises": results
        }), 200

    except NoBodyPartsSelected as e:
        return jsonify({
            "success": False,
            "errorType": "NoBodyPartsSelected",
            "message": str(e)
        }), 400

    except NoMusclesSelected as e:
        return jsonify({
            "success": False,
            "errorType": "NoMusclesSelected",
            "message": str(e)
        }), 400

    except InvalidMuscleSelection as e:
        return jsonify({
            "success": False,
            "errorType": "InvalidMuscleSelection",
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "errorType": "ServerError",
            "message": f"Unexpected error: {str(e)}"
        }), 500


@app.route("/api/get_muscles_for_parts", methods=["POST"])
@require_auth
def api_get_muscles_for_parts():
    """Returns the list of muscles available for given body parts"""
    data = request.get_json() or {}
    body_parts = data.get("bodyParts", [])
    allowed = list_muscles_for_body_parts(body_parts)
    
    return jsonify({
        "success": True,
        "muscles": allowed
    }), 200


# Find Classes Route (Protected)
@app.route("/find-classes", methods=["POST"])
@require_auth
def find_classes_route():
    data = request.get_json()
    campus = data.get("campus")
    categories = data.get("categories")

    try:
        results = find_classes(campus, categories)
        return jsonify({"classes": results}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


# Server Startup
if __name__ == "__main__":
    PORT = 5001
    print("\n" + "="*60)
    print("🐾 SPOTTER SERVER STARTING")
    print("="*60)
    print(f"📁 Serving files from: {FRONTEND_DIR}")
    print(f"🌐 Open your browser to: http://localhost:{PORT}")
    print(f"🌐 Or try: http://127.0.0.1:{PORT}")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=PORT)

