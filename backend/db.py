from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Database URL
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["spotter-db"] 

# Collections
users = db.users
sessions = db.sessions
friend_requests = db.friend_requests
friendships = db.friendships
challenges = db.challenges
workouts = db.workouts
challenge_participants = db.challenge_participants
feed_posts = db.feed_posts

# Create indexes for better performance and uniqueness
try:
    users.create_index("email", unique=True)
    sessions.create_index("token", unique=True)
    sessions.create_index("expires_at")
    challenges.create_index("creator")
    challenges.create_index("created_at")
    workouts.create_index("creator")
    workouts.create_index("created_at")
    friend_requests.create_index([("from_user", 1), ("to_user", 1)], unique=True)
    friendships.create_index([("user1", 1), ("user2", 1)], unique=True)
    print("MongoDB indexes created successfully")
except Exception as e:
    print(f"Note: Some indexes may already exist - {e}")


# Friend-related functions
def search_users(query, current_user_email, limit=20):
    """Search for users by email or username"""
    if not query or len(query.strip()) == 0:
        return []
    
    # Search by email or username (case-insensitive)
    search_results = users.find({
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"username": {"$regex": query, "$options": "i"}}
        ],
        "email": {"$ne": current_user_email}  # Exclude current user
    }).limit(limit)
    
    results = []
    for user in search_results:
        # Check friendship status
        is_friend = check_friendship(current_user_email, user["email"])
        has_pending_request = check_pending_request(current_user_email, user["email"])
        
        results.append({
            "email": user["email"],
            "username": user.get("username", user["email"].split("@")[0]),
            "bio": user.get("bio", ""),
            "is_friend": is_friend,
            "has_pending_request": has_pending_request
        })
    
    return results


def check_friendship(user1_email, user2_email):
    """Check if two users are friends"""
    friendship = friendships.find_one({
        "$or": [
            {"user1": user1_email, "user2": user2_email},
            {"user1": user2_email, "user2": user1_email}
        ]
    })
    return friendship is not None


def check_pending_request(from_user, to_user):
    """Check if there's a pending friend request"""
    request = friend_requests.find_one({
        "from_user": from_user,
        "to_user": to_user,
        "status": "pending"
    })
    return request is not None


def send_friend_request(from_user_email, to_user_email):
    """Send a friend request"""
    # Check if users exist
    from_user = users.find_one({"email": from_user_email})
    to_user = users.find_one({"email": to_user_email})
    
    if not from_user or not to_user:
        return False, "User not found"
    
    # Check if already friends
    if check_friendship(from_user_email, to_user_email):
        return False, "Already friends"
    
    # Check if request already exists
    if check_pending_request(from_user_email, to_user_email):
        return False, "Friend request already sent"
    
    # Check if there's a reverse pending request
    if check_pending_request(to_user_email, from_user_email):
        return False, "This user has already sent you a friend request"
    
    # Create friend request
    friend_requests.insert_one({
        "from_user": from_user_email,
        "to_user": to_user_email,
        "status": "pending",
        "created_at": datetime.utcnow()
    })
    
    return True, "Friend request sent"


def get_friend_requests(user_email):
    """Get all pending friend requests for a user"""
    requests = friend_requests.find({
        "to_user": user_email,
        "status": "pending"
    }).sort("created_at", -1)
    
    result = []
    for req in requests:
        from_user = users.find_one({"email": req["from_user"]})
        if from_user:
            result.append({
                "request_id": str(req["_id"]),
                "from_email": req["from_user"],
                "from_username": from_user.get("username", req["from_user"].split("@")[0]),
                "created_at": req["created_at"]
            })
    
    return result


def accept_friend_request(request_from, request_to):
    """Accept a friend request"""
    # Update request status
    result = friend_requests.update_one(
        {"from_user": request_from, "to_user": request_to, "status": "pending"},
        {"$set": {"status": "accepted", "accepted_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        return False, "Friend request not found"
    
    # Create friendship (store in alphabetical order to avoid duplicates)
    user1, user2 = sorted([request_from, request_to])
    
    friendships.insert_one({
        "user1": user1,
        "user2": user2,
        "created_at": datetime.utcnow()
    })
    
    return True, "Friend request accepted"


def reject_friend_request(request_from, request_to):
    """Reject a friend request"""
    result = friend_requests.update_one(
        {"from_user": request_from, "to_user": request_to, "status": "pending"},
        {"$set": {"status": "rejected", "rejected_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        return False, "Friend request not found"
    
    return True, "Friend request rejected"


def get_friends(user_email):
    """Get all friends of a user"""
    friends_list = friendships.find({
        "$or": [
            {"user1": user_email},
            {"user2": user_email}
        ]
    }).sort("created_at", -1)
    
    result = []
    for friendship in friends_list:
        # Get the other user's email
        friend_email = friendship["user2"] if friendship["user1"] == user_email else friendship["user1"]
        
        # Get friend's details
        friend = users.find_one({"email": friend_email})
        if friend:
            result.append({
                "email": friend_email,
                "username": friend.get("username", friend_email.split("@")[0]),
                "bio": friend.get("bio", ""),
                "friends_since": friendship["created_at"]
            })
    
    return result


def remove_friend(user_email, friend_email):
    """Remove a friend"""
    user1, user2 = sorted([user_email, friend_email])
    
    result = friendships.delete_one({
        "user1": user1,
        "user2": user2
    })
    
    if result.deleted_count == 0:
        return False, "Friendship not found"
    
    return True, "Friend removed"

# functions for profile

def get_user_profile(email):
    """Get user profile information"""
    user = users.find_one({"email": email})
    
    if not user:
        return None
    
    # Get user stats
    stats = get_user_stats(email)
    
    return {
        "email": email,
        "username": user.get("username", email.split("@")[0]),
        "bio": user.get("bio", ""),
        "profile_picture": user.get("profile_picture", ""),
        "joined_date": user.get("created_at", datetime.utcnow()),
        "favorite_workout": user.get("favorite_workout", ""),
        "fitness_goal": user.get("fitness_goal", ""),
        "stats": stats
    }


def update_user_profile(email, data):
    """Update user profile information"""
    allowed_fields = ["username", "bio", "profile_picture", "favorite_workout", "fitness_goal"]
    
    update_data = {}
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    if not update_data:
        return False, "No valid fields to update"
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = users.update_one(
        {"email": email},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        return True, "Profile updated successfully"
    else:
        return False, "No changes made"


def get_user_stats(email):
    """Calculate user statistics"""
    # Count challenges created
    challenges_created = challenges.count_documents({"creator": email})
    
    # Count challenges participated in
    challenges_joined = challenge_participants.count_documents({"participant_email": email})
    
    # Count workouts logged
    workouts_logged = workouts.count_documents({"creator": email})
    
    # Count friends
    friends_count = friendships.count_documents({
        "$or": [
            {"user1": email},
            {"user2": email}
        ]
    })
    
    # Calculate total workout duration
    workout_pipeline = [
        {"$match": {"creator": email}},
        {"$group": {
            "_id": None,
            "total_duration": {"$sum": "$duration"},
            "total_calories": {"$sum": "$calories"}
        }}
    ]
    
    workout_stats = list(workouts.aggregate(workout_pipeline))
    total_duration = workout_stats[0]["total_duration"] if workout_stats else 0
    total_calories = workout_stats[0]["total_calories"] if workout_stats else 0
    
    # Get workout streak (days with at least one workout)
    recent_workouts = list(workouts.find(
        {"creator": email}
    ).sort("date", -1).limit(30))
    
    streak = calculate_streak(recent_workouts)
    
    return {
        "challenges_created": challenges_created,
        "challenges_joined": challenges_joined,
        "workouts_logged": workouts_logged,
        "total_workout_minutes": total_duration,
        "total_calories_burned": total_calories,
        "friends_count": friends_count,
        "current_streak": streak
    }


def calculate_streak(workouts):
    """Calculate the current workout streak in days"""
    if not workouts:
        return 0
    
    from datetime import timedelta
    
    # Get unique workout dates
    workout_dates = set()
    for workout in workouts:
        workout_date = workout.get("date")
        if isinstance(workout_date, str):
            workout_date = datetime.strptime(workout_date, "%Y-%m-%d").date()
        elif isinstance(workout_date, datetime):
            workout_date = workout_date.date()
        workout_dates.add(workout_date)
    
    if not workout_dates:
        return 0
    
    # Sort dates in descending order
    sorted_dates = sorted(workout_dates, reverse=True)
    
    # Check if the most recent workout was today or yesterday
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    if sorted_dates[0] not in [today, yesterday]:
        return 0
    
    # Count consecutive days
    streak = 1
    expected_date = sorted_dates[0] - timedelta(days=1)
    
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break
    
    return streak


def get_user_recent_activities(email, limit=10):
    """Get user's recent activities (challenges and workouts)"""
    activities = []
    
    # Get recent challenges
    user_challenges = challenges.find(
        {"creator": email}
    ).sort("created_at", -1).limit(limit)
    
    for challenge in user_challenges:
        activities.append({
            "type": "challenge",
            "data": {
                "id": str(challenge["_id"]),
                "title": challenge["title"],
                "goal": challenge["goal"],
                "created_at": challenge["created_at"],
                "privacy": challenge.get("privacy", "public")
            }
        })
    
    # Get recent workouts
    user_workouts = workouts.find(
        {"creator": email}
    ).sort("created_at", -1).limit(limit)
    
    for workout in user_workouts:
        activities.append({
            "type": "workout",
            "data": {
                "id": str(workout["_id"]),
                "workout_name": workout["workout_name"],
                "workout_type": workout["workout_type"],
                "duration": workout["duration"],
                "created_at": workout["created_at"],
                "privacy": workout.get("privacy", "public")
            }
        })
    
    # Sort by creation date and limit
    activities.sort(key=lambda x: x["data"]["created_at"], reverse=True)
    return activities[:limit]