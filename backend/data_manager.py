# backend/data_manager.py
# Handles all data storage using MongoDB

from db import challenges, workouts
from datetime import datetime


def load_challenges():
    """Load all challenges from MongoDB"""
    try:
        # Convert MongoDB cursor to list and remove _id field
        challenge_list = list(challenges.find({}, {"_id": 0}).sort("created_at", -1))
        return challenge_list
    except Exception as e:
        print(f"Error loading challenges: {e}")
        return []


def save_challenges(challenge_list):
    """This function is no longer needed with MongoDB, but kept for compatibility"""
    return True


def get_challenge_by_id(challenge_id):
    """Get a specific challenge by ID"""
    return challenges.find_one({"id": challenge_id}, {"_id": 0})


def get_public_challenges():
    """Get all public challenges"""
    return list(challenges.find({"privacy": "public"}, {"_id": 0}).sort("created_at", -1))


def get_challenges_by_creator(email):
    """Get challenges created by a specific user"""
    return list(challenges.find({"creator": email}, {"_id": 0}).sort("created_at", -1))


def add_challenge(challenge):
    """Add a new challenge to MongoDB"""
    try:
        challenges.insert_one(challenge)
        return True
    except Exception as e:
        print(f"Error adding challenge: {e}")
        return False


# Workout Data Operations
def load_workouts():
    """Load all workouts from MongoDB"""
    try:
        workout_list = list(workouts.find({}, {"_id": 0}).sort("created_at", -1))
        return workout_list
    except Exception as e:
        print(f"Error loading workouts: {e}")
        return []


def save_workouts(workout_list):
    """This function is no longer needed with MongoDB, but kept for compatibility"""
    return True


def get_workout_by_id(workout_id):
    """Get a specific workout by ID"""
    return workouts.find_one({"id": workout_id}, {"_id": 0})


def get_workouts_by_creator(email):
    """Get workouts created by a specific user"""
    return list(workouts.find({"creator": email}, {"_id": 0}).sort("created_at", -1))


def add_workout(workout):
    """Add a new workout to MongoDB"""
    try:
        workouts.insert_one(workout)
        return True
    except Exception as e:
        print(f"Error adding workout: {e}")
        return False


# Combined Activity Feed
def get_all_activities():
    """Get all PUBLIC activities (challenges and workouts) sorted by creation time"""
    try:
        # Get only public challenges and workouts
        all_challenges = list(challenges.find({"privacy": "public"}, {"_id": 0}))
        all_workouts = list(workouts.find({"privacy": "public"}, {"_id": 0}))
        
        # Combine and sort by created_at timestamp, newest first
        all_activities = all_challenges + all_workouts
        all_activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return all_activities
    except Exception as e:
        print(f"Error loading activities: {e}")
        return []


def get_user_activities(email):
    """Get all activities (public and private) for a specific user"""
    try:
        user_challenges = list(challenges.find({"creator": email}, {"_id": 0}))
        user_workouts = list(workouts.find({"creator": email}, {"_id": 0}))
        
        all_activities = user_challenges + user_workouts
        all_activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return all_activities
    except Exception as e:
        print(f"Error loading user activities: {e}")
        return []


def get_friends_activities(email_list):
    """Get all PUBLIC activities from a list of users (self + friends)"""
    try:
        # Get public challenges and workouts from the specified users
        friend_challenges = list(challenges.find({
            "creator": {"$in": email_list},
            "privacy": "public"
        }, {"_id": 0}))
        
        friend_workouts = list(workouts.find({
            "creator": {"$in": email_list},
            "privacy": "public"
        }, {"_id": 0}))
        
        # Combine and sort by created_at timestamp, newest first
        all_activities = friend_challenges + friend_workouts
        all_activities.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return all_activities
    except Exception as e:
        print(f"Error loading friends activities: {e}")
        return []
