from database.mongo_connection import users_collection
from model.user import user_helper, UserSchema
from bson import ObjectId
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from database.mongo_connection import redis

SECRET_KEY = 'secret'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwt_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')

async def register(user_data: UserSchema) -> dict:
    user = await users_collection.find_one({'username': user_data['username']})
    print(user)
    if not user:
        user_data['created_at'] = datetime.utcnow()
        user_data['password'] = pwt_context.hash(user_data['password'])
        user = await users_collection.insert_one(user_data)
        new_user = await users_collection.find_one({'_id': user.inserted_id})
        return user_helper(new_user)
    return None

async def login(username: str, password: str):
    user = await users_collection.find_one({'username': username})
    if pwt_context.verify(password, user['password']):
        token = generate_token({'username': user['username']})
        update_jwt = {'jwt_token': token}
        await users_collection.update_one({'username': user['username']}, {'$set': update_jwt})
        return token
    return None

def generate_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(to_encode)
    return encoded_jwt

async def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    cached_user = await redis.get(payload['username'])
    if not cached_user:
        user = await users_collection.find_one({'username': payload['username']})
        redis.set(payload['username'], user, expire=1800)
    else:
        user = cached_user

    if user and user['jwt_token'] == token:
        return user_helper(user)
    return False

async def update_password(username: str, old_password: str, new_password: str):
    user = await users_collection.find_one({'username': username})
    if await pwt_context.verify(old_password, user['password']):
        updated_user = await users_collection.update_one(
            {'username': user['username']}, {'$set': {'password': pwt_context.hash(new_password)}}
        )
        return True
    return False

async def reset_password(username: str) -> dict:
    user = await users_collection.find_one({'username': username})
    if user:
        updated_user = await users_collection.update_one(
            {'username': username}, {'$set': {'password': '123456789'}}
        )
        if updated_user:
            return True
        return False
    return False