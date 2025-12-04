from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Database URL
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["spotter-db"] 

# Collections
users = db.users
sessions = db.sessions  # For session management
friend_requests = db.friend_requests
friendships = db.friendships
challenges = db.challenges
workouts = db.workouts  # Add this line
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
    print("MongoDB indexes created successfully")
except Exception as e:
    print(f"Note: Some indexes may already exist - {e}")