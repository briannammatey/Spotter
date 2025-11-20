from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
# Configure CORS to allow requests from frontend
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# In-memory data storage (replace with database in production)
exercises_db = {
    "arms": {
        "biceps": ["Barbell Curl", "Hammer Curl", "Cable Curl", "Concentration Curl"],
        "triceps": ["Tricep Dips", "Overhead Extension", "Close-Grip Bench Press", "Tricep Pushdown"],
        "forearms": ["Wrist Curl", "Reverse Wrist Curl", "Farmer's Walk"]
    },
    "legs": {
        "quadriceps": ["Squat", "Leg Press", "Leg Extension", "Lunges"],
        "hamstrings": ["Romanian Deadlift", "Leg Curl", "Good Morning"],
        "calves": ["Calf Raise", "Seated Calf Raise", "Jump Rope"],
        "glutes": ["Hip Thrust", "Glute Bridge", "Bulgarian Split Squat"],
        "abductors": ["Side Leg Raise", "Clamshell", "Hip Abduction Machine"]
    },
    "chest": {
        "pectorals": ["Bench Press", "Push-ups", "Chest Fly", "Incline Dumbbell Press"],
        "upper_chest": ["Incline Bench Press", "Incline Fly"]
    },
    "back": {
        "lats": ["Pull-ups", "Lat Pulldown", "Bent-Over Row", "T-Bar Row"],
        "rhomboids": ["Face Pull", "Reverse Fly", "Cable Row"],
        "traps": ["Shrug", "Upright Row", "High Pull"]
    },
    "shoulders": {
        "deltoids": ["Overhead Press", "Lateral Raise", "Front Raise", "Rear Delt Fly"],
        "rotator_cuff": ["External Rotation", "Internal Rotation"]
    },
    "abs": {
        "rectus_abdominis": ["Crunches", "Plank", "Leg Raises", "Russian Twist"],
        "obliques": ["Side Plank", "Bicycle Crunch", "Woodchopper"]
    }
}

class_types = ["BOXING", "CARDIO", "CYCLING", "DANCE", "PILATES", "YOGA", "STRENGTH", "HIIT", "SPINNING"]

recipes_db = {
    "breakfast": {
        "lose_weight": ["Greek Yogurt with Berries", "Oatmeal with Banana", "Egg White Scramble"],
        "gain_weight": ["Protein Pancakes", "Avocado Toast with Eggs", "Breakfast Burrito"],
        "build_muscle": ["Protein Smoothie Bowl", "Eggs with Whole Grain Toast", "Chicken and Sweet Potato"]
    },
    "lunch": {
        "lose_weight": ["Grilled Chicken Salad", "Quinoa Bowl with Vegetables", "Turkey Wrap"],
        "gain_weight": ["Chicken and Rice Bowl", "Beef Stir Fry", "Pasta with Meat Sauce"],
        "build_muscle": ["Salmon with Brown Rice", "Lean Beef with Vegetables", "Tuna Salad Sandwich"]
    },
    "dinner": {
        "lose_weight": ["Baked Salmon with Vegetables", "Turkey Meatballs with Zucchini Noodles", "Grilled Chicken with Broccoli"],
        "gain_weight": ["Steak with Potatoes", "Pork Chops with Rice", "Chicken Alfredo"],
        "build_muscle": ["Grilled Chicken Breast with Sweet Potato", "Lean Beef with Quinoa", "Fish with Brown Rice"]
    },
    "dessert": {
        "lose_weight": ["Greek Yogurt with Honey", "Dark Chocolate", "Fruit Salad"],
        "gain_weight": ["Protein Brownies", "Ice Cream", "Cheesecake"],
        "build_muscle": ["Protein Pudding", "Greek Yogurt Parfait", "Chocolate Protein Shake"]
    },
    "snack": {
        "lose_weight": ["Apple with Almond Butter", "Carrot Sticks with Hummus", "Greek Yogurt"],
        "gain_weight": ["Trail Mix", "Protein Bar", "Peanut Butter Sandwich"],
        "build_muscle": ["Protein Shake", "Cottage Cheese with Fruit", "Nuts and Seeds"]
    }
}

# Store for user data
workouts = []
challenges = []

@app.route('/api/weightlifting-suggestions', methods=['POST'])
def weightlifting_suggestions():
    """Operation Contract 1: weightliftingSuggetsions()"""
    try:
        data = request.json
        body_parts = data.get('body_parts', [])
        muscles = data.get('muscles', [])
        
        if not body_parts:
            return jsonify({'error': 'Please select at least one body part'}), 400
        
        suggested_exercises = []
        
        # If specific muscles are selected, use those
        if muscles:
            for body_part in body_parts:
                body_part_lower = body_part.lower()
                if body_part_lower in exercises_db:
                    for muscle in muscles:
                        muscle_lower = muscle.lower()
                        if muscle_lower in exercises_db[body_part_lower]:
                            suggested_exercises.extend(exercises_db[body_part_lower][muscle_lower])
        else:
            # Otherwise, get all exercises for selected body parts
            for body_part in body_parts:
                body_part_lower = body_part.lower()
                if body_part_lower in exercises_db:
                    for muscle_group, exercises in exercises_db[body_part_lower].items():
                        suggested_exercises.extend(exercises)
        
        if not suggested_exercises:
            return jsonify({'error': 'No exercises found for selected criteria'}), 404
        
        # Create routine with sets, reps, rest time
        routine = []
        for exercise in list(set(suggested_exercises))[:10]:  # Limit to 10 unique exercises
            routine.append({
                'exercise': exercise,
                'sets': 3,
                'reps': 10,
                'rest_time': '60 seconds'
            })
        
        return jsonify({
            'success': True,
            'routine': routine,
            'message': 'Routine generated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercise-class-suggestions', methods=['POST'])
def exercise_class_suggestions():
    """Operation Contract 2: exerciseClassSuggestions()"""
    try:
        data = request.json
        liked_classes = data.get('liked_classes', [])
        disliked_classes = data.get('disliked_classes', [])
        distance = data.get('distance', '5 miles')
        location = data.get('location', 'on_campus')  # 'on_campus' or 'off_campus'
        
        # Filter out disliked classes
        available_classes = [c for c in class_types if c not in disliked_classes]
        
        # If user has liked classes, prioritize similar types
        if liked_classes:
            # Simple matching: suggest classes similar to liked ones
            suggestions = []
            for liked in liked_classes:
                if liked in available_classes:
                    suggestions.append({
                        'name': f'{liked} Class',
                        'location': 'BU FitRec' if location == 'on_campus' else 'Local Gym',
                        'distance': distance,
                        'time': '6:00 PM',
                        'instructor': 'TBA'
                    })
        else:
            # Suggest popular classes
            popular = [c for c in available_classes if c in ['CARDIO', 'YOGA', 'STRENGTH']]
            suggestions = []
            for cls in popular[:3]:
                suggestions.append({
                    'name': f'{cls} Class',
                    'location': 'BU FitRec' if location == 'on_campus' else 'Local Gym',
                    'distance': distance,
                    'time': '6:00 PM',
                    'instructor': 'TBA'
                })
        
        if not suggestions:
            return jsonify({'error': 'No classes found matching your preferences'}), 404
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'message': f'Found {len(suggestions)} class suggestions'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log-workout', methods=['POST'])
def log_workout():
    """Operation Contract 3: logWorkout()"""
    try:
        data = request.json
        print(f"Received workout data: {data}")  # Debug log
        description = data.get('description', '').strip()
        privacy = data.get('privacy')  # 'private' or 'public'
        photo_url = data.get('photo_url', '')
        personal_record = data.get('personal_record', '')
        user_id = data.get('user_id', 'default_user')
        saved_to_profile = data.get('saved_to_profile', False)  # Flag to indicate if saved to profile
        
        if not description:
            return jsonify({'error': 'Please enter a description of your workout'}), 400
        
        if privacy not in ['private', 'public']:
            return jsonify({'error': 'Please select whether the workout should be private or public'}), 400
        
        workout = {
            'id': len(workouts) + 1,
            'description': description,
            'privacy': privacy,
            'photo_url': photo_url,
            'personal_record': personal_record,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'saved_to_profile': saved_to_profile  # Track if this was saved to profile
        }
        
        workouts.append(workout)
        print(f"Workout saved. Total workouts: {len(workouts)}, User ID: {user_id}, Saved to profile: {saved_to_profile}")  # Debug log
        print(f"All workouts: {workouts}")  # Debug log
        
        return jsonify({
            'success': True,
            'message': 'Workout saved successfully',
            'workout': workout
        })
    except Exception as e:
        print(f"Error saving workout: {e}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-challenge', methods=['POST'])
def create_challenge():
    """Operation Contract 4: createChallenge()"""
    try:
        data = request.json
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        description = data.get('description', '').strip()
        privacy = data.get('privacy')  # 'private' or 'public'
        goals = data.get('goals', [])
        friends = data.get('friends', [])
        routine_id = data.get('routine_id')
        
        # Validation
        if not start_date or not end_date:
            return jsonify({'error': 'Please enter both start and end dates'}), 400
        
        if not description:
            return jsonify({'error': 'Please enter a challenge description'}), 400
        
        if privacy not in ['private', 'public']:
            return jsonify({'error': 'Please select whether the challenge should be private or public'}), 400
        
        # Validate dates
        try:
            start = datetime.strptime(start_date, '%m/%d/%Y')
            end = datetime.strptime(end_date, '%m/%d/%Y')
            if start >= end:
                return jsonify({'error': 'Start date must be before end date'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date format. Please use MM/DD/YYYY'}), 400
        
        challenge = {
            'id': len(challenges) + 1,
            'start_date': start_date,
            'end_date': end_date,
            'description': description,
            'privacy': privacy,
            'goals': goals,
            'friends': friends,
            'routine_id': routine_id,
            'timestamp': datetime.now().isoformat(),
            'user_id': data.get('user_id', 'default_user')
        }
        
        challenges.append(challenge)
        print(f"Challenge saved. Total challenges: {len(challenges)}, User ID: {challenge.get('user_id')}")  # Debug log
        print(f"All challenges: {challenges}")  # Debug log
        
        return jsonify({
            'success': True,
            'message': 'Challenge created successfully',
            'challenge': challenge
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recipe-suggestion', methods=['POST'])
def provide_recipe_suggestion():
    """Operation Contract 5: provideRecipeSugesstion()"""
    try:
        data = request.json
        meal_type = data.get('meal_type', '').lower()
        fitness_goal = data.get('fitness_goal', '').lower().replace(' ', '_')
        
        if not meal_type:
            return jsonify({'error': 'Please select a type of meal'}), 400
        
        if not fitness_goal:
            return jsonify({'error': 'Please select your fitness goals'}), 400
        
        # Map fitness goals
        goal_map = {
            'lose_weight': 'lose_weight',
            'gain_weight': 'gain_weight',
            'build_muscle': 'build_muscle'
        }
        
        if fitness_goal not in goal_map:
            return jsonify({'error': 'Invalid fitness goal selected'}), 400
        
        fitness_goal = goal_map[fitness_goal]
        
        if meal_type not in recipes_db:
            return jsonify({'error': 'Invalid meal type selected'}), 400
        
        if fitness_goal not in recipes_db[meal_type]:
            return jsonify({'error': 'No recipes found for this combination'}), 404
        
        recipes = recipes_db[meal_type][fitness_goal]
        selected_recipe = recipes[0] if recipes else None
        
        if not selected_recipe:
            return jsonify({'error': 'No recipe matches the selected criteria'}), 404
        
        recipe_details = {
            'name': selected_recipe,
            'meal_type': meal_type,
            'fitness_goal': fitness_goal,
            'ingredients': [
                'Protein source (chicken, fish, or plant-based)',
                'Complex carbohydrates',
                'Healthy fats',
                'Vegetables'
            ],
            'instructions': [
                'Prepare ingredients according to recipe',
                'Cook following standard preparation methods',
                'Serve and enjoy'
            ],
            'nutrition_info': {
                'calories': '300-500',
                'protein': '25-35g',
                'carbs': '30-50g',
                'fats': '10-15g'
            }
        }
        
        return jsonify({
            'success': True,
            'recipe': recipe_details,
            'message': 'Recipe suggestion generated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/muscles', methods=['GET'])
def get_muscles():
    """Get available muscles for a body part"""
    body_part = request.args.get('body_part', '').lower()
    if body_part in exercises_db:
        muscles = list(exercises_db[body_part].keys())
        return jsonify({'muscles': muscles})
    return jsonify({'muscles': []})

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    """Get all workouts for a user (only those saved to profile)"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        print(f"Fetching workouts for user_id: {user_id}")  # Debug log
        print(f"Total workouts in memory: {len(workouts)}")  # Debug log
        print(f"All workouts: {workouts}")  # Debug log
        
        # Filter by user_id and only include workouts saved to profile
        user_workouts = [w for w in workouts if w.get('user_id') == user_id and w.get('saved_to_profile', False)]
        print(f"Found {len(user_workouts)} workout(s) saved to profile for user {user_id}")  # Debug log
        
        # Sort by timestamp, most recent first
        user_workouts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({
            'success': True,
            'workouts': user_workouts
        })
    except Exception as e:
        print(f"Error fetching workouts: {e}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges', methods=['GET'])
def get_challenges():
    """Get all challenges for a user"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        print(f"Fetching challenges for user_id: {user_id}")  # Debug log
        print(f"Total challenges in memory: {len(challenges)}")  # Debug log
        print(f"All challenges: {challenges}")  # Debug log
        
        user_challenges = [c for c in challenges if c.get('user_id') == user_id]
        print(f"Found {len(user_challenges)} challenge(s) for user {user_id}")  # Debug log
        
        # Sort by timestamp, most recent first
        user_challenges.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({
            'success': True,
            'challenges': user_challenges
        })
    except Exception as e:
        print(f"Error fetching challenges: {e}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug():
    """Debug endpoint to check server status and data"""
    return jsonify({
        'status': 'Server is running',
        'total_workouts': len(workouts),
        'total_challenges': len(challenges),
        'workouts': workouts,
        'challenges': challenges
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

