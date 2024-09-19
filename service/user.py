from database.mongo_connection import users_collection
from model.user import user_helper, UserSchema
from bson import ObjectId
from utils.makequery import makequery

async def retrive_users():
    users = []
    async for user in users_collection.find():
        users.append(user_helper(user))
    return users

async def retrive_user(username: str) -> dict:
    user = await users_collection.find_one({'username': username})
    if user:
        return user_helper(user)
    return None

async def update_user(id: str, data: dict) -> dict:
    if len(data) < 1:
        return False
    user = await users_collection.find_one({'_id': ObjectId(id)})
    if user:
        updated_user = await users_collection.update_one(
            {'_id': ObjectId(id)}, {'$set': data}
        )
        if updated_user:
            return True
        return False
    return None

async def delete_user(id: str):
    user = await users_collection.find_one({'_id': ObjectId(id)})
    if user:
        await users_collection.delete_one({'_id': ObjectId(id)})
        return True
    return False

async def retrive_users_by_city(city: str, query = None):
    filter = makequery(query, {'selectedcity': city})
    users = []
    async for user in users_collection.find(filter):
        users.append(user_helper(user))
    return users