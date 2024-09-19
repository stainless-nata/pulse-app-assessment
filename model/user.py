from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserSchema(BaseModel):
    firstname: str
    lastname: str
    username: str
    password: str
    profilepic: str
    created_at: Optional[datetime] = None
    jwt_token: Optional[str] = None
    selectedcity: str

class UserCreditional(BaseModel):
    username: str
    password: str

def user_helper(user) -> dict:
    return {
        'id': str(user['_id']),
        'firstname': user['firstname'],
        'lastname': user['lastname'],
        'username': user['username'],
        'profilepic': user['profilepic'],
        'created_at': user['created_at'],
        'selectedcity': user['selectedcity'],
    }