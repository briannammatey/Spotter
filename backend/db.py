from pymongo import MongoClient
from secrets import MONGODB_URL

#database url

client = MongoClient(MONGO_URL)

db = client["spotter-db"] 

users = db.users
friend_requests = db.friend_requests
friendships = db.friendships
challenges = db.challenges
challenge_participants = db.challenge_participants
feed_posts = db.feed_posts
