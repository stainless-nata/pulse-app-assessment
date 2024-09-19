import service.friend as FriendService
from fastapi import APIRouter, Body, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from model.friendrequest import FriendRequestSchema
from utils.responsetype import response
from typing import Union
from utils.limiter import limiter

router = APIRouter()

@router.get('/')
@limiter.limit("15/minute")
async def get_all_friends(request: Request):
    user = request.state.user
    if user:
        friends = await FriendService.retrive_friends(user['id'])
        return response(message='friends', data=friends)
    raise HTTPException(401, detail='unauthorized')

@router.post('/')
@limiter.limit("15/minute")
async def friend_request(friend: FriendRequestSchema, request: Request):
    user = request.state.user
    friend = friend.dict()
    if user['id'] == friend['senderId']:
        new_friend = await FriendService.add_friend(friend)
        print(new_friend)
        return response(message='friend requested', data=new_friend)
    else:
        raise HTTPException(401, detail='unauthorized')

@router.get('/pending')
@limiter.limit("15/minute")
async def get_friend_requested(request: Request):
    user = request.state.user
    if user:
        friends = await FriendService.retrive_pending_requests(user['id'])
        return response(message='friend requested', data=friends)
    else:
        raise HTTPException(401, detail='unauthorized')

@router.get('/not')
@limiter.limit("15/minute")
async def get_not_friends(request: Request):
    user = request.state.user
    if user:
        not_friends = await FriendService.retrive_not_friends(user['id'])
        return response(message="not friends", data=not_friends)
    else:
        raise HTTPException(401, detail='unauthorized')