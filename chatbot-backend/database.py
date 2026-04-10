from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

# Connect to MongoDB Atlas
client = AsyncIOMotorClient(MONGO_URL)

# Your database name is "chatbot"
db = client.chatbot

# Two collections — like two tables
users_collection = db.users
messages_collection = db.messages
chats_collection = db.chats