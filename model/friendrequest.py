from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FriendRequestSchema(BaseModel):
    senderId: str
    receiverId: str
    status: str = 'not received'
    created_at: Optional[datetime] = None

def friend_helper(friend) -> dict:
    return {
        'id': str(friend['_id']),
        'senderId': str(friend['senderId']),
        'receiverId': str(friend['receiverId']),
        'status': friend['status'],
        'created_at': friend['created_at'],
    }