# Spotter Backend Application
from dotenv import load_dotenv 
load_dotenv()
from db import users, friend_requests, friendships, challenges, challenge_participants


import os
print("Loaded API key:", os.environ.get("OPENAI_API_KEY"))

from recipeSuggestions.suggest import generate_day_plan
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from create_Challenge import create_challenge
from logWorkout import log_workout
from data_manager import (load_challenges, get_public_challenges, get_challenge_by_id,load_workouts, get_workout_by_id, get_all_activities)
from getExercises import (generate_exercises, list_muscles_for_body_parts, NoBodyPartsSelected, NoMusclesSelected, InvalidMuscleSelection)

# Get the path to the frontend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # project root
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')  # project_root/frontend
IMG_DIR = os.path.join(PROJECT_ROOT, 'img')  # project_root/img

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

# API Routes - Recipe Generation
@app.route("/api/recipe-plan", methods=["POST"])
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
  
# API Routes - Exercise Generation
@app.route("/api/generate_exercises", methods=["POST"])
def api_generate_exercises():
    """
    Generate exercises based on selected body parts and muscles.
    Expects JSON:
    {
        "bodyParts": [...],
        "muscles": [...]
    }
    """

    data = request.get_json() or {}

    body_parts = data.get("bodyParts", [])
    muscles = data.get("muscles", [])

    try:
        # Call AI generator
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
        # Catch-all for unexpected errors
        return jsonify({
            "success": False,
            "errorType": "ServerError",
            "message": f"Unexpected error: {str(e)}"
        }), 500
    
# API Routes - Generates list of muscles
@app.route("/api/get_muscles_for_parts", methods=["POST"])
def api_get_muscles_for_parts():
    """
    Returns the list of muscles available for given body parts.
    Expects JSON:
    {
        "bodyParts": [...]
    }
    """

    data = request.get_json() or {}
    body_parts = data.get("bodyParts", [])

    allowed = list_muscles_for_body_parts(body_parts)

    return jsonify({
        "success": True,
        "muscles": allowed
    }), 200

@app.route("/api/users/create", methods=["POST"])
def create_user():
    data = request.get_json()
    result = users.insert_one(data)
    return jsonify({"user_id": str(result.inserted_id)}), 201

@app.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    return jsonify(user), 200 if user else 404

# Friends
@app.route("/api/friends/request/send", methods=["POST"])
def send_request():
    data = request.get_json()
    friend_requests.insert_one({"senderId": data["senderId"], "receiverId": data["receiverId"], "status": "pending"})
    return jsonify({"status": "request sent"}), 201

@app.route("/api/friends/request/accept", methods=["POST"])
def accept_request():
    data = request.get_json()
    friend_requests.update_one({"senderId": data["senderId"], "receiverId": data["receiverId"]}, {"$set": {"status": "accepted"}})
    friendships.insert_one({"userId": data["senderId"], "friendId": data["receiverId"]})
    friendships.insert_one({"userId": data["receiverId"], "friendId": data["senderId"]})
    return jsonify({"status": "request accepted"}), 200

@app.route("/api/friends/<user_id>", methods=["GET"])
def list_friends(user_id):
    friends = list(friendships.find({"userId": user_id}))
    for f in friends:
        f["_id"] = str(f["_id"])
    return jsonify(friends), 200

# Challenges
@app.route("/api/challenges/create", methods=["POST"])
def create_challenge():
    data = request.get_json()
    result = challenges.insert_one(data)
    return jsonify({"challenge_id": str(result.inserted_id)}), 201

@app.route("/api/challenges/<challenge_id>/invite", methods=["POST"])
def invite_friend(challenge_id):
    data = request.get_json()
    challenge_participants.insert_one({"challengeId": challenge_id, "userId": data["friendId"], "invitedBy": data["invitedBy"], "status": "invited"})
    return jsonify({"status": "friend invited"}), 200

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
