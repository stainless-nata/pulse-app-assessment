from fastapi import APIRouter, Body, HTTPException, Request
import service.auth as AuthService
from model.user import UserSchema, UserCreditional
from datetime import datetime
from utils.responsetype import response
from utils.limiter import limiter

router = APIRouter()

@router.post('/signup')
@limiter.limit("2/minute")
async def signup(user: UserSchema, request: Request):
    user_data = user.dict()
    user = await AuthService.register(user_data)
    if not user:
        raise HTTPException(status_code=404, detail='username already exists')
    return response(message='user registered successfully', data=user)

@router.post('/signin')
@limiter.limit("2/minute")
async def signin(creditional: UserCreditional, request: Request):
    cre = creditional.dict()
    token = await AuthService.login(cre['username'], cre['password'])
    if not token:
        raise HTTPException(status_code=404, detail='username or password is incorrect.')
    return response(message='token', data={'token': token})
    