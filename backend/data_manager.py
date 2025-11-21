# Data Manager Module
# Handles all data storage


import json
import os

# Path to store data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CHALLENGES_FILE = os.path.join(DATA_DIR, 'challenges.json')
WORKOUTS_FILE = os.path.join(DATA_DIR, 'workouts.json')

# Create data directory if doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize data files if don't exist
if not os.path.exists(CHALLENGES_FILE):
    with open(CHALLENGES_FILE, 'w') as f:
        json.dump([], f)

if not os.path.exists(WORKOUTS_FILE):
    with open(WORKOUTS_FILE, 'w') as f:
        json.dump([], f)

def load_challenges():
    """Load all challenges from the JSON file"""
    try:
        with open(CHALLENGES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading challenges: {e}")
        return []

def save_challenges(challenges):
    """Save challenges to the JSON file"""
    try:
        with open(CHALLENGES_FILE, 'w') as f:
            json.dump(challenges, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving challenges: {e}")
        return False

def get_challenge_by_id(challenge_id):
    """Get a specific challenge by ID"""
    challenges = load_challenges()
    return next((c for c in challenges if c['id'] == challenge_id), None)

def get_public_challenges():
    """Get all public challenges"""
    challenges = load_challenges()
    return [c for c in challenges if c.get('privacy') == 'public']

def add_challenge(challenge):
    """Add a new challenge to the beginning of the list"""
    challenges = load_challenges()
    challenges.insert(0, challenge)
    return save_challenges(challenges)


# Workout Data Operations
def load_workouts():
    """Load all workouts from the JSON file"""
    try:
        with open(WORKOUTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading workouts: {e}")
        return []

def save_workouts(workouts):
    """Save workouts to the JSON file"""
    try:
        with open(WORKOUTS_FILE, 'w') as f:
            json.dump(workouts, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving workouts: {e}")
        return False

def get_workout_by_id(workout_id):
    """Get a specific workout by ID"""
    workouts = load_workouts()
    return next((w for w in workouts if w['id'] == workout_id), None)

def add_workout(workout):
    """Add a new workout to the beginning of the list"""
    workouts = load_workouts()
    workouts.insert(0, workout)
    return save_workouts(workouts)


# Combined Activity Feed
def get_all_activities():
    """Get all activities (challenges and workouts) sorted by creation time"""
    challenges = get_public_challenges()
    workouts = load_workouts()
    
    # Combine and sort by created_at timestamp, newest is first
    all_activities = challenges + workouts
    all_activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return all_activities
