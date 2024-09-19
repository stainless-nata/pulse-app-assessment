from service.user import retrive_users, retrive_user, delete_user, update_user
from fastapi import APIRouter, Body, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from model.user import UserSchema
from utils.responsetype import response
from typing import Union
from utils.limiter import limiter

router = APIRouter()

@router.get('/')
@limiter.limit("15/minute")
async def get_all_users(request: Request):
    users = await retrive_users()
    return response(message='user registered successfully', data=users)

@router.get('/profile')
@limiter.limit("15/minute")
async def profile(request: Request):
    user = request.state.user
    if user:
        return response(message='profile', data=user)
    raise HTTPException(401, detail='unauthorized')

@router.get('/{username}')
@limiter.limit("15/minute")
async def get_user(username: str, request: Request):
    user = await retrive_user(username)
    print(request.state.user)
    return response(message='users in your city', data=user)