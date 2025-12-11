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