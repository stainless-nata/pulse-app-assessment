from fastapi import HTTPException
from fastapi import FastAPI, HTTPException, Depends, Request
from router.auth import router as auth_router
from router.user import router as user_router
from router.city import router as city_router
from router.friend import router as friend_router
import service.auth as AuthService
from jose import ExpiredSignatureError
from database.mongo_connection import redis
from utils.limiter import init_limiter
from datetime import datetime
from middleware.time import TimingMiddleware

app = FastAPI()

init_limiter(app)

async def authorize_user(request: Request):
    token = request.headers.get('authorization')
    token = token.split(' ')[1]
    if not token:
        raise HTTPException(status_code=400, detail='Token Not Found')
    try:
        user = await AuthService.verify_token(token)
        if not user:
            raise HTTPException(status_code=400, detail='Invalid Token')
        request.state.user = user
        return request
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='Token Expired')

app.include_router(auth_router, tags=['auth'], prefix='/api/auth')
app.include_router(user_router, tags=['user'], prefix='/api/user', dependencies=[Depends(authorize_user)])
app.include_router(city_router, tags=['city'], prefix='/api/city', dependencies=[Depends(authorize_user)])
app.include_router(friend_router, tags=['friend'], prefix='/api/friend', dependencies=[Depends(authorize_user)])

app.add_middleware(TimingMiddleware)

@app.get('/', tags=['Root'])
async def read_root():
    return {'message': 'Welcome to this fantastic app!'}