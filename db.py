import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ASCENDING, IndexModel

from models import OTP, User

load_dotenv()


client = AsyncIOMotorClient(os.getenv("MONGO_URI"))

db = client[os.getenv("MONGO_DB_NAME")]
print(f"Connecting to MongoDB URI: {os.getenv('MONGO_URI')}")

users_collection: AsyncIOMotorCollection[User] = db["users"]
otp_collection: AsyncIOMotorCollection[OTP] = db["otps"]

user_index = IndexModel([("email", ASCENDING)], unique=True)
users_collection.create_indexes([user_index])
