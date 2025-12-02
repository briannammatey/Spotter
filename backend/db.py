from pymongo import MongoClient


#database url
MONGO_URL = "mongodb+srv://briianna_db_user:EMJ1Xurwv5FlZelQ@spotter-db.j6xscen.mongodb.net/?appName=spotter-db"

client = MongoClient(MONGO_URL)

db = client["spotter-db"] 

users = db.users
friend_requests = db.friend_requests
friendships = db.friendships
challenges = db.challenges
challenge_participants = db.challenge_participants
feed_posts = db.feed_posts
