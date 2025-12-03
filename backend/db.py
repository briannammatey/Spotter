from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
#database url
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["spotter-db"] 

users = db.users
friend_requests = db.friend_requests
friendships = db.friendships
challenges = db.challenges
challenge_participants = db.challenge_participants
feed_posts = db.feed_posts
