from database.mongo_connection import friends_collection, users_collection
from model.friendrequest import friend_helper, FriendRequestSchema
from model.user import user_helper
import service.user as UserService
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from database.mongo_connection import redis
import json

async def cache_data(key, data, expire=1800):
    await redis.set(key, json.dumps(data), expire=expire)

async def get_cached_data(key):
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    return None

async def add_friend(friend_data):
    already_friend = await friends_collection.find_one({'senderId': ObjectId(friend_data['senderId']), 'receiverId': ObjectId(friend_data['receiverId'])})
    if already_friend:
        raise HTTPException(401, detail='Already friend or requested')
    
    await redis.delete(f"friends:{friend_data['senderId']}")
    await redis.delete(f"friends:{friend_data['receiverId']}")

    friend = await friends_collection.find_one({'receiverId': ObjectId(friend_data['senderId']), 'senderId': ObjectId(friend_data['receiverId'])})
    if not friend:
        friend_data['senderId'] = ObjectId(friend_data['senderId'])
        friend_data['receiverId'] = ObjectId(friend_data['receiverId'])
        friend_data['created_at'] = datetime.utcnow()
        friend_data['status'] = 'not received'
        new_friend = await friends_collection.insert_one(friend_data)
        new_friend = await friends_collection.find_one({'_id': new_friend.inserted_id})
        return friend_helper(new_friend)
    elif friend['status'] != 'received':
        friend['status'] = 'received'
        updated_friend = await friends_collection.update_one(
            {'_id': ObjectId(friend['_id'])},
            {'$set': {'status': 'received'}}
        )
        updated_friend = await friends_collection.find_one({'_id': ObjectId(friend['_id'])})
        print(updated_friend)
        return friend_helper(updated_friend)
    else:
        raise HTTPException(401, detail='Already friend')

async def retrive_friends(user_id: str):
    cache_key = f"friends:{user_id}"
    cached_friends = await get_cached_data(cache_key)
    if cached_friends:
        return cached_friends
    
    filter = {
        '$and': [
            {'$or': [{'receiverId': ObjectId(user_id)}, {'senderId': ObjectId(user_id)}]},
            {'status': 'received'}
        ]
    }
    friend_requests = []
    async for request in friends_collection.find(filter):
        friend_requests.append(friend_helper(request))
    users = []
    for request in friend_requests:
        if user_id == request['receiverId']:
            users.append(user_helper(await users_collection.find_one({'_id': ObjectId(request['senderId'])})))
        else:
            users.append(user_helper(await users_collection.find_one({'_id': ObjectId(request['receiverId'])})))
    await cache_data(cache_key, users)
    return users

async def retrive_pending_requests(user_id: str):
    filter = {
        '$and': [
            {'$or': [{'receiverId': ObjectId(user_id)}, {'senderId': ObjectId(user_id)}]},
            {'status': 'not received'}
        ]
    }
    friend_requests = []
    async for request in friends_collection.find(filter):
        friend_requests.append(friend_helper(request))
    users = []
    for request in friend_requests:
        users.append(user_helper(await users_collection.find_one({'_id': ObjectId(request['senderId'])})))
    return users

async def retrive_not_friends(user_id: str):
    cache_key = f"non_friends:{user_id}"
    cached_non_friends = await get_cached_data(cache_key)
    if cached_non_friends:
        return cached_non_friends
    
    friends_query = {
        "$or": [
            {"senderId": ObjectId(user_id), "status": "received"},
            {"receiverId": ObjectId(user_id), "status": "received"}
        ]
    }

    friend_ids = set()
    async for friend in friends_collection.find(friends_query):
        if friend["senderId"] != ObjectId(user_id):
            friend_ids.add(friend["senderId"])
        if friend["receiverId"] != ObjectId(user_id):
            friend_ids.add(friend["receiverId"])
    
    non_friends_query = {
        "_id": {"$nin": list(friend_ids), "$ne": ObjectId(user_id)}
    }

    non_friends_list = []
    async for user in users_collection.find(non_friends_query):
        non_friends_list.append(user_helper(user))

    await cache_data(cache_key, non_friends_list)
    return non_friends_list