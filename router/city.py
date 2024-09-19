import service.user as UserService
from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from model.user import UserSchema
from utils.responsetype import response
from typing import Union
from utils.limiter import limiter

router = APIRouter()

@router.get('/users-in-mycity')
@limiter.limit("15/minute")
async def get_all_users_in_my_city(request: Request):
    user = request.state.user
    users_in_mycity = await UserService.retrive_users_by_city(user['selectedcity'], request.query_params)
    return response('users in my city', users_in_mycity)

@router.get('/{city_name}/user')
@limiter.limit("15/minute")
async def get_all_users_in_city(city_name: str, request: Request):
    users_in_mycity = await UserService.retrive_users_by_city(city_name, request.query_params)
    return response(message='user registered successfully', data=users_in_mycity)
