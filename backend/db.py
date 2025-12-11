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
likes = db.likes
comments = db.comments
challenge_invitations = db.challenge_invitations

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
    likes.create_index([("user_email", 1), ("post_id", 1), ("post_type", 1)], unique=True)
    comments.create_index("post_id")
    comments.create_index("created_at")
    challenge_invitations.create_index([("challenge_id", 1), ("invitee_email", 1)], unique=True)
    challenge_invitations.create_index("invitee_email")
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
# Add these functions to your db.py file

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


# Likes and Comments Functions
def add_like(user_email, post_id, post_type):
    """Add a like to a post (workout or challenge)"""
    try:
        # Check if already liked
        existing = likes.find_one({
            "user_email": user_email,
            "post_id": post_id,
            "post_type": post_type
        })
        
        if existing:
            return False, "Already liked"
        
        likes.insert_one({
            "user_email": user_email,
            "post_id": post_id,
            "post_type": post_type,
            "created_at": datetime.utcnow()
        })
        
        return True, "Like added"
    except Exception as e:
        return False, str(e)


def remove_like(user_email, post_id, post_type):
    """Remove a like from a post"""
    try:
        result = likes.delete_one({
            "user_email": user_email,
            "post_id": post_id,
            "post_type": post_type
        })
        
        if result.deleted_count > 0:
            return True, "Like removed"
        else:
            return False, "Like not found"
    except Exception as e:
        return False, str(e)


def get_likes_for_post(post_id, post_type):
    """Get all likes for a specific post"""
    try:
        like_list = list(likes.find({
            "post_id": post_id,
            "post_type": post_type
        }))
        
        # Get user details for each like
        likes_with_users = []
        for like in like_list:
            user = users.find_one({"email": like["user_email"]})
            if user:
                likes_with_users.append({
                    "user_email": like["user_email"],
                    "username": user.get("username", like["user_email"].split("@")[0]),
                    "created_at": like["created_at"]
                })
        
        return likes_with_users
    except Exception as e:
        return []


def get_like_count(post_id, post_type):
    """Get the number of likes for a post"""
    return likes.count_documents({
        "post_id": post_id,
        "post_type": post_type
    })


def has_user_liked(user_email, post_id, post_type):
    """Check if a user has liked a post"""
    return likes.find_one({
        "user_email": user_email,
        "post_id": post_id,
        "post_type": post_type
    }) is not None


def add_comment(user_email, post_id, post_type, comment_text):
    """Add a comment to a post"""
    try:
        user = users.find_one({"email": user_email})
        
        comment = {
            "user_email": user_email,
            "username": user.get("username", user_email.split("@")[0]) if user else user_email,
            "post_id": post_id,
            "post_type": post_type,
            "comment_text": comment_text,
            "created_at": datetime.utcnow()
        }
        
        result = comments.insert_one(comment)
        comment["_id"] = str(result.inserted_id)
        
        return True, "Comment added", comment
    except Exception as e:
        return False, str(e), None


def get_comments_for_post(post_id, post_type):
    """Get all comments for a specific post"""
    try:
        comment_list = list(comments.find({
            "post_id": post_id,
            "post_type": post_type
        }).sort("created_at", -1))
        
        # Convert ObjectId to string
        for comment in comment_list:
            comment["_id"] = str(comment["_id"])
        
        return comment_list
    except Exception as e:
        return []


def get_comment_count(post_id, post_type):
    """Get the number of comments for a post"""
    return comments.count_documents({
        "post_id": post_id,
        "post_type": post_type
    })


def delete_comment(comment_id, user_email):
    """Delete a comment (only if user is the comment author)"""
    try:
        from bson import ObjectId
        result = comments.delete_one({
            "_id": ObjectId(comment_id),
            "user_email": user_email
        })
        
        if result.deleted_count > 0:
            return True, "Comment deleted"
        else:
            return False, "Comment not found or not authorized"
    except Exception as e:
        return False, str(e)


def get_friends_and_self_emails(user_email):
    """Get list of emails including user and their friends"""
    emails = [user_email]
    
    # Get all friendships
    friends_list = friendships.find({
        "$or": [
            {"user1": user_email},
            {"user2": user_email}
        ]
    })
    
    for friendship in friends_list:
        friend_email = friendship["user2"] if friendship["user1"] == user_email else friendship["user1"]
        emails.append(friend_email)
    
    return emails


# Challenge Invitation Functions
def send_challenge_invitation(challenge_id, challenge_title, inviter_email, invitee_email):
    """Send a challenge invitation to a user"""
    try:
        # Check if invitation already exists
        existing = challenge_invitations.find_one({
            "challenge_id": challenge_id,
            "invitee_email": invitee_email
        })
        
        if existing:
            return False, "Already invited"
        
        # Get inviter details
        inviter = users.find_one({"email": inviter_email})
        inviter_username = inviter.get("username", inviter_email.split("@")[0]) if inviter else inviter_email
        
        challenge_invitations.insert_one({
            "challenge_id": challenge_id,
            "challenge_title": challenge_title,
            "inviter_email": inviter_email,
            "inviter_username": inviter_username,
            "invitee_email": invitee_email,
            "status": "pending",
            "created_at": datetime.utcnow()
        })
        
        return True, "Invitation sent"
    except Exception as e:
        return False, str(e)


def get_challenge_invitations(user_email):
    """Get all pending challenge invitations for a user"""
    try:
        invitations = list(challenge_invitations.find({
            "invitee_email": user_email,
            "status": "pending"
        }).sort("created_at", -1))
        
        # Convert ObjectId to string
        for invitation in invitations:
            invitation["_id"] = str(invitation["_id"])
        
        return invitations
    except Exception as e:
        return []


def accept_challenge_invitation(challenge_id, user_email):
    """Accept a challenge invitation"""
    try:
        # Update invitation status
        result = challenge_invitations.update_one(
            {"challenge_id": challenge_id, "invitee_email": user_email, "status": "pending"},
            {"$set": {"status": "accepted", "accepted_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            return False, "Invitation not found"
        
        # Add user to challenge participants
        challenge_participants.insert_one({
            "challenge_id": challenge_id,
            "participant_email": user_email,
            "joined_at": datetime.utcnow()
        })
        
        # Update challenge participants count
        challenges.update_one(
            {"id": challenge_id},
            {"$inc": {"participants": 1}}
        )
        
        return True, "Challenge invitation accepted"
    except Exception as e:
        return False, str(e)


def decline_challenge_invitation(challenge_id, user_email):
    """Decline a challenge invitation"""
    try:
        result = challenge_invitations.update_one(
            {"challenge_id": challenge_id, "invitee_email": user_email, "status": "pending"},
            {"$set": {"status": "declined", "declined_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            return False, "Invitation not found"
        
        return True, "Challenge invitation declined"
    except Exception as e:
        return False, str(e)
