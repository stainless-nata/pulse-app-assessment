from pymongo import MongoClient
from redis.asyncio import Redis
import motor.motor_asyncio


MONGO_USERNAME = 'mytest'
MONGO_PASSWORD = '123456789'
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'test'

client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}')

database = client.test

users_collection = database.get_collection('users')
friends_collection = database.get_collection('friendrequests')

redis = Redis(host='localhost', port=6379, db=0)