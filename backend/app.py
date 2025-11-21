# Spotter Backend Application
from dotenv import load_dotenv 
load_dotenv()

import os
print("Loaded API key:", os.environ.get("OPENAI_API_KEY"))

from recipeSuggestions.suggest import generate_day_plan
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from createChallenge import create_challenge
from logWorkout import log_workout
from data_manager import (load_challenges, get_public_challenges, get_challenge_by_id,load_workouts, get_workout_by_id, get_all_activities)

# Get the path to the frontend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # project root
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')  # project_root/frontend

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)


@app.route('/')
def index():
    """Serve the homepage"""
    try:
        return send_from_directory(app.static_folder, 'homepage.html')
    except Exception as e:
        print(f"Error serving homepage: {e}")
        return f"Error: {e}", 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        print(f"Error serving {path}: {e}")
        return f"File not found: {path}", 404


# API Routes - Challenge Management
@app.route("/api/create_challenge", methods=["POST"])
def api_create_challenge():
    """
    Create a new challenge
    """
    data = request.get_json()
    success, result, status_code = create_challenge(data)
    return jsonify(result), status_code

@app.route("/api/challenges", methods=["GET"])
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

@app.route("/api/activities", methods=["GET"])
def api_get_activities():
    """
    Get all activities for the feed
    """
    try:
        # Get all activities (challenges and workouts)
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


# API Routes - Workout Management
@app.route("/api/log_workout", methods=["POST"])
def api_log_workout():
    """
    Log a new workout
    """
    data = request.get_json()
    success, result, status_code = log_workout(data)
    return jsonify(result), status_code

@app.route("/api/workouts", methods=["GET"])
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

# API Routes - Future Features (wait to be implemented)
@app.route("/api/recipe-plan", methods=["POST"])
def recipe_plan():
    data = request.get_json() or {}
    print("Incoming recipe request:", data)

    try:
        plan = generate_day_plan(
            goal=data.get("goal"),
            diet=data.get("diet"),
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



# TODO: Add recipe generation routes
# @app.route("/api/generate_recipe", methods=["POST"])
# def api_generate_recipe():
#     pass

# TODO: Add user authentication routes
# @app.route("/api/login", methods=["POST"])
# @app.route("/api/register", methods=["POST"])
# @app.route("/api/logout", methods=["POST"])


# Server Startup


if __name__ == "__main__":
    PORT = 5001  # Using port 5001
    print("\n" + "="*60)
    print("🐾 SPOTTER SERVER STARTING")
    print("="*60)
    print(f"📁 Serving files from: {FRONTEND_DIR}")
    print(f"🌐 Open your browser to: http://localhost:{PORT}")
    print(f"🌐 Or try: http://127.0.0.1:{PORT}")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=PORT)
